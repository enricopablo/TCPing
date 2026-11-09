import pytest

from tcping.stats import calculate_stats


def test_calculate_stats_empty():
    assert calculate_stats([]) == (0, 0, 0, 0)


def test_calculate_stats_single_value_has_zero_jitter():
    assert calculate_stats([10.0]) == (10.0, 10.0, 10.0, 0)
    assert isinstance(calculate_stats([10.0])[3], float)  # JSON: 0.0, not 0


def test_calculate_stats_values():
    avg, min_lat, max_lat, jitter = calculate_stats([10.0, 20.0, 30.0])
    assert avg == 20.0
    assert min_lat == 10.0
    assert max_lat == 30.0
    assert jitter == pytest.approx(10.0)  # sample standard deviation


from tcping.stats import summarize  # noqa: E402


def test_summarize_with_success():
    s = summarize(2, 1, [10.0, 20.0], 3.456)
    assert s["attempts"] == 3
    assert s["success"] == 2
    assert s["failed"] == 1
    assert s["success_rate"] == 66.67
    assert s["latency_ms"] == {"min": 10.0, "avg": 15.0, "max": 20.0, "jitter": 7.07}
    assert s["duration_s"] == 3.46


def test_summarize_all_failed_has_no_latency():
    s = summarize(0, 2, [], 1.0)
    assert s["success_rate"] == 0.0
    assert s["latency_ms"] is None


def test_summarize_no_attempts():
    s = summarize(0, 0, [], 0.0)
    assert s["attempts"] == 0
    assert s["success_rate"] is None
