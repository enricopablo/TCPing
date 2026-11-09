import statistics


def calculate_stats(latencies):
    if not latencies:
        return 0.0, 0.0, 0.0, 0.0
    avg_lat = sum(latencies) / len(latencies)
    min_lat = min(latencies)
    max_lat = max(latencies)
    jitter = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
    return avg_lat, min_lat, max_lat, jitter


def summarize(success_count, fail_count, latencies, duration_s):
    """Resumo da execução (valores arredondados em 2 casas).

    `success_rate` é None sem tentativas; `latency_ms` é None sem sucessos.
    """
    attempts = success_count + fail_count
    latency = None
    if latencies:
        avg_lat, min_lat, max_lat, jitter = calculate_stats(latencies)
        latency = {
            "min": round(min_lat, 2),
            "avg": round(avg_lat, 2),
            "max": round(max_lat, 2),
            "jitter": round(jitter, 2),
        }
    return {
        "attempts": attempts,
        "success": success_count,
        "failed": fail_count,
        "success_rate": round(success_count / attempts * 100, 2) if attempts else None,
        "latency_ms": latency,
        "duration_s": round(duration_s, 2),
    }
