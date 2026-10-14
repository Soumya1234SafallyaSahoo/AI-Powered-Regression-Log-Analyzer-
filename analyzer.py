"""Rule-based analysis for synthetic regression logs."""
from collections import Counter
import re
from typing import Any

ERROR_PATTERNS = [
    ("timeout", re.compile(r"\b(timeout|timed out)\b", re.I)),
    ("assertion_failure", re.compile(r"\b(assertion failed|assertion error|assert failed)\b", re.I)),
    ("connection_error", re.compile(r"\b(connection refused|connection reset|connection error)\b", re.I)),
    ("memory_error", re.compile(r"\b(out of memory|oom|memory allocation failed)\b", re.I)),
    ("compile_error", re.compile(r"\b(compile error|compilation failed|syntax error)\b", re.I)),
]
FAIL_PATTERN = re.compile(r"\b(FAIL|FAILED|ERROR)\b", re.I)
WARN_PATTERN = re.compile(r"\b(WARN|WARNING)\b", re.I)

def analyze_log(log_text: str) -> dict[str, Any]:
    """Summarize a log using transparent rules; does not claim definitive root cause."""
    lines = [line.strip() for line in log_text.splitlines() if line.strip()]
    failures = [line for line in lines if FAIL_PATTERN.search(line)]
    warnings = [line for line in lines if WARN_PATTERN.search(line)]

    categories = Counter()
    evidence = []
    for line in lines:
        for category, pattern in ERROR_PATTERNS:
            if pattern.search(line):
                categories[category] += 1
                evidence.append({"category": category, "line": line})
                break

    suggestions = {
        "timeout": "Check service responsiveness, configured timeout, and whether the test environment is overloaded.",
        "assertion_failure": "Compare expected and actual values; inspect the test setup and the first failing assertion.",
        "connection_error": "Check host/port configuration, service availability, firewall rules, and network connectivity.",
        "memory_error": "Inspect memory usage, input size, resource limits, and possible leaks.",
        "compile_error": "Review the compiler or tool output immediately before the first compilation error.",
    }
    likely_causes = [
        {"category": category, "count": count, "debugging_hint": suggestions[category]}
        for category, count in categories.most_common()
    ]

    status = "failed" if failures or evidence else ("warnings" if warnings else "no_obvious_failure")
    return {
        "status": status,
        "total_nonempty_lines": len(lines),
        "failure_lines": failures,
        "warning_lines": warnings,
        "error_categories": dict(categories),
        "evidence": evidence,
        "possible_causes_and_hints": likely_causes,
        "note": "Heuristic analysis only. Suggested causes are not confirmed diagnoses.",
    }
