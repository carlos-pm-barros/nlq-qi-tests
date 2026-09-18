from statistics import mean, stdev
from src.app.models import QualityGate

def calculate_gate(scores: list[float], min_average: float,
                   min_item: float, max_stddev: float) -> QualityGate:
    avg = mean(scores)
    minimum = min(scores)
    deviation = stdev(scores) if len(scores) > 1 else 0.0
    failures = []
    if avg < min_average:
        failures.append(f"average {avg:.4f} < {min_average:.4f}")
    if minimum < min_item:
        failures.append(f"minimum {minimum:.4f} < {min_item:.4f}")
    if deviation > max_stddev:
        failures.append(f"stddev {deviation:.4f} > {max_stddev:.4f}")
    return QualityGate(
        average=avg, minimum=minimum, stddev=deviation,
        passed=not failures, failures=failures
    )
