import socket

import pytest

from tcping.target import Target, build_targets, parse_targets, target_label


def test_parse_single_host_and_port():
    assert parse_targets(["google.com", "443"]) == (["google.com"], [443])


def test_parse_combinations():
    assert parse_targets(["web1", "web2", "80", "443"]) == (["web1", "web2"], [80, 443])


def test_parse_ip_is_host_not_port():
    assert parse_targets(["1.1.1.1", "53"]) == (["1.1.1.1"], [53])


def test_parse_removes_duplicates_keeping_order():
    assert parse_targets(["b", "a", "b", "443", "80", "443"]) == (["b", "a"], [443, 80])


@pytest.mark.parametrize(
    "args, message",
    [
        (["443"], "at least one host"),
        (["google.com"], "at least one port"),
        (["google.com", "0"], "Invalid port"),
        (["google.com", "70000"], "Invalid port"),
    ],
)
def test_parse_errors(args, message):
    with pytest.raises(ValueError, match=message):
        parse_targets(args)


def test_target_label_ipv6_brackets():
    assert target_label("::1", 443) == "[::1]:443"
    assert target_label("google.com", 443) == "google.com:443"


def test_build_targets_cartesian_product():
    targets = build_targets(["127.0.0.1", "localhost"], [80, 443], socket.AF_INET)
    assert [t.label for t in targets] == [
        "127.0.0.1:80",
        "127.0.0.1:443",
        "localhost:80",
        "localhost:443",
    ]
    assert [t.sockaddr for t in targets[:2]] == [("127.0.0.1", 80), ("127.0.0.1", 443)]


def test_build_targets_dns_error_marks_all_ports_of_host():
    targets = build_targets(["host-inexistente.invalid", "127.0.0.1"], [80, 443])
    assert [t.error for t in targets] == [
        "Host not found",
        "Host not found",
        None,
        None,
    ]


def test_target_record_and_history():
    t = Target("x", 1)
    for ok in [True, False] * 6:
        t.record(ok, 5.0 if ok else None, None if ok else "Timeout")
    assert t.success_count == 6
    assert t.fail_count == 6
    assert len(t.history) == 10  # only the last 10
    assert t.last == (False, None, "Timeout")
    assert t.summary(1.0)["latency_ms"]["avg"] == 5.0
