"""LLM-backed misconception reasoning.

Provider-agnostic entry point `llm_diagnose(...)`. Currently implements Gemini
(free tier) via its REST API using only the stdlib, so there's no SDK
dependency to manage. Ollama can be added behind the same interface later by
switching on LLM_PROVIDER.

All failures (no key, network, rate-limit, bad JSON) return None so the caller
falls back to AST-only diagnosis — the LLM is never a hard dependency.
"""
from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request

log = logging.getLogger(__name__)

# Gemini occasionally returns 503/429 under load; a couple of quick retries
# smooths over those transient blips without making the user wait long.
RETRY_STATUSES = {429, 500, 503}
MAX_ATTEMPTS = 3

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

PROMPT_TEMPLATE = """You are a {language} tutor diagnosing the single root misconception behind a \
first-year student's failing solution. Do not just restate the test failure — name the \
underlying thinking error.

PROBLEM: {title}
{description}

STUDENT CODE ({language}):
```
{code}
```

OBSERVED FAILURE:
{failure}

KNOWN MISCONCEPTIONS (choose the best-matching code, or "none" if none fit):
{catalog}

Respond with ONLY a JSON object of this exact shape:
{{"misconception_code": "<one code from the list or 'none'>",
  "confidence": <float 0..1>,
  "explanation": "<=2 sentences, address the student directly, explain the actual error>",
  "fix_hint": "<one concrete sentence on how to fix it>"}}"""


def _build_prompt(code: str, problem: dict, failure: str, catalog: list[dict],
                  language: str = "python") -> str:
    catalog_lines = "\n".join(
        f'- {m["code"]}: {m["name"]} (concept: {m["concept"]})' for m in catalog
    )
    return PROMPT_TEMPLATE.format(
        language=language,
        title=problem.get("title", ""),
        description=(problem.get("description", "") or "")[:1500],
        code=code[:4000],
        failure=failure[:1500] or "Output did not match the expected result.",
        catalog=catalog_lines,
    )


def _call_gemini(prompt: str, timeout: int = 30) -> str | None:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    if not key:
        log.info("GEMINI_API_KEY not set — skipping LLM diagnosis.")
        return None

    url = GEMINI_URL.format(model=model, key=key)
    body = json.dumps(
        {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2,
            },
        }
    ).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = json.load(urllib.request.urlopen(req, timeout=timeout))
            return resp["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as exc:
            if exc.code in RETRY_STATUSES and attempt < MAX_ATTEMPTS:
                log.info("Gemini %s (attempt %d) — retrying.", exc.code, attempt)
                time.sleep(0.8 * attempt)
                continue
            log.warning("Gemini HTTP %s: %s", exc.code, exc.reason)
            return None
        except (urllib.error.URLError, KeyError, IndexError, ValueError) as exc:
            log.warning("Gemini call failed: %s", exc)
            return None
    return None


def llm_diagnose(code: str, problem: dict, failure: str, catalog: list[dict],
                 language: str = "python") -> dict | None:
    """Return {misconception_code, confidence, explanation, fix_hint} or None."""
    provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
    if provider != "gemini":
        log.info("LLM_PROVIDER=%s not implemented yet — skipping.", provider)
        return None

    raw = _call_gemini(_build_prompt(code, problem, failure, catalog, language))
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except ValueError:
        log.warning("LLM returned non-JSON: %.120s", raw)
        return None

    code_val = (data.get("misconception_code") or "").strip()
    if not code_val or code_val.lower() == "none":
        return {
            "misconception_code": None,
            "confidence": float(data.get("confidence", 0) or 0),
            "explanation": data.get("explanation", ""),
            "fix_hint": data.get("fix_hint", ""),
        }
    return {
        "misconception_code": code_val,
        "confidence": float(data.get("confidence", 0) or 0),
        "explanation": data.get("explanation", ""),
        "fix_hint": data.get("fix_hint", ""),
    }
