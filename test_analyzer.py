from app.analyzer import analyze_log

def test_detects_timeout_and_failure():
    result = analyze_log("INFO start\nERROR: test timed out\nTEST FAILED")
    assert result["status"] == "failed"
    assert result["error_categories"]["timeout"] == 1
    assert result["failure_lines"]

def test_warning_without_failure():
    result = analyze_log("INFO started\nWARNING: retrying")
    assert result["status"] == "warnings"
    assert len(result["warning_lines"]) == 1

def test_clean_log():
    result = analyze_log("INFO start\nINFO all checks passed")
    assert result["status"] == "no_obvious_failure"
