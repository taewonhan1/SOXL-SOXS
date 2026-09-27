"""Minimal Massive (formerly Polygon.io) REST client.

* Base URL https://api.massive.com ; authentication is injected by the network proxy, so the client
  never adds an ``apiKey`` parameter.
* Retries with exponential backoff + jitter on 429 / 5xx / connection errors, honours Retry-After.
* Follows ``next_url`` pagination.
* A module-level semaphore bounds concurrency (<= 6; default 4) because the API key is shared.
"""
from __future__ import annotations

import os
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Iterable

import requests

from . import config

os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")

_local = threading.local()
_SEM = threading.BoundedSemaphore(min(6, max(1, config.MAX_CONCURRENCY)))

RETRY_STATUS = {429, 500, 502, 503, 504}


def _session() -> requests.Session:
    s = getattr(_local, "session", None)
    if s is None:
        s = requests.Session()
        s.headers.update({"User-Agent": "soxlab/0.1"})
        _local.session = s
    return s


class ApiResponse:
    """Thin wrapper so callers can inspect status codes without exceptions (used by the probe)."""

    def __init__(self, status: int, payload: Any, url: str, elapsed: float):
        self.status = status
        self.payload = payload
        self.url = url
        self.elapsed = elapsed

    @property
    def ok(self) -> bool:
        return self.status == 200

    def json(self) -> Any:
        return self.payload


def get(path_or_url: str, params: dict | None = None, *, retries: int = 6, timeout: float = 90.0,
        raise_for_status: bool = True) -> ApiResponse:
    """GET with retry/backoff. ``path_or_url`` may be a path ('/v2/...') or a full next_url."""
    url = path_or_url if path_or_url.startswith("http") else config.API_BASE + path_or_url
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        t0 = time.time()
        try:
            with _SEM:
                r = _session().get(url, params=params, timeout=timeout)
            elapsed = time.time() - t0
            if r.status_code in RETRY_STATUS and attempt < retries:
                ra = r.headers.get("Retry-After")
                wait = float(ra) if ra and ra.replace(".", "", 1).isdigit() else min(60.0, 1.5 * 2 ** attempt)
                time.sleep(wait + random.uniform(0, 0.5))
                continue
            try:
                payload = r.json()
            except ValueError:
                payload = {"_text": r.text[:2000]}
            resp = ApiResponse(r.status_code, payload, r.url, elapsed)
            if raise_for_status and r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code} for {r.url}: {str(payload)[:300]}")
            return resp
        except (requests.ConnectionError, requests.Timeout, requests.exceptions.ChunkedEncodingError) as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(min(60.0, 1.5 * 2 ** attempt) + random.uniform(0, 0.5))
                continue
            raise
    raise RuntimeError(f"exhausted retries for {url}: {last_exc}")


def get_all(path: str, params: dict | None = None, *, max_pages: int = 10_000,
            results_key: str = "results") -> list[dict]:
    """Collect ``results`` across ``next_url`` pages."""
    out: list[dict] = []
    resp = get(path, params)
    page = 1
    while True:
        js = resp.json()
        out.extend(js.get(results_key) or [])
        nxt = js.get("next_url")
        if not nxt or page >= max_pages:
            break
        resp = get(nxt)
        page += 1
    return out


def parallel_map(fn: Callable, items: Iterable, max_workers: int | None = None,
                 desc: str = "", verbose: bool = True) -> list:
    """Run ``fn`` over ``items`` in a thread pool (concurrency additionally capped by the semaphore)."""
    items = list(items)
    workers = max_workers or config.MAX_CONCURRENCY
    results: list = [None] * len(items)
    done = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fn, it): i for i, it in enumerate(items)}
        for fut in as_completed(futs):
            i = futs[fut]
            results[i] = fut.result()
            done += 1
            if verbose and (done % 25 == 0 or done == len(items)):
                print(f"  [{desc}] {done}/{len(items)} done in {time.time() - t0:.0f}s", flush=True)
    return results
