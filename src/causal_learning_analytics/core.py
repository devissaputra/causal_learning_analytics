from collections.abc import Sequence


def _validate_inputs(
    treatment: Sequence[int],
    outcome: Sequence[float],
    propensity: Sequence[float],
) -> None:
    if not treatment or not (len(treatment) == len(outcome) == len(propensity)):
        raise ValueError("inputs must be non-empty and have equal length")
    if any(value not in (0, 1) for value in treatment):
        raise ValueError("treatment must contain only 0 and 1")
    if any(not 0.0 <= value <= 1.0 for value in propensity):
        raise ValueError("propensity scores must be between 0 and 1")


def ipw_ate(
    treatment: Sequence[int],
    outcome: Sequence[float],
    propensity: Sequence[float],
    clip: float = 0.05,
) -> float:
    """Estimate an average treatment effect with Horvitz-Thompson IPW."""
    _validate_inputs(treatment, outcome, propensity)
    if not 0.0 < clip < 0.5:
        raise ValueError("clip must be between 0 and 0.5")

    scores = [min(1 - clip, max(clip, value)) for value in propensity]
    treated = [y / p for t, y, p in zip(treatment, outcome, scores) if t == 1]
    control = [y / (1 - p) for t, y, p in zip(treatment, outcome, scores) if t == 0]
    if not treated or not control:
        raise ValueError("both treatment groups must be present")

    sample_size = len(treatment)
    return sum(treated) / sample_size - sum(control) / sample_size


def overlap_fraction(
    propensity: Sequence[float], lower: float = 0.1, upper: float = 0.9
) -> float:
    """Return the share of scores inside a simple overlap region."""
    if not propensity:
        raise ValueError("propensity must not be empty")
    if not 0.0 <= lower < upper <= 1.0:
        raise ValueError("overlap bounds must satisfy 0 <= lower < upper <= 1")
    if any(not 0.0 <= value <= 1.0 for value in propensity):
        raise ValueError("propensity scores must be between 0 and 1")
    return sum(lower <= value <= upper for value in propensity) / len(propensity)


def standardized_mean_difference(
    treatment: Sequence[int], values: Sequence[float]
) -> float:
    """Return the standardized mean difference between two treatment groups."""
    if not treatment or len(treatment) != len(values):
        raise ValueError("treatment and values must be non-empty and have equal length")
    if any(value not in (0, 1) for value in treatment):
        raise ValueError("treatment must contain only 0 and 1")

    treated = [value for flag, value in zip(treatment, values) if flag == 1]
    control = [value for flag, value in zip(treatment, values) if flag == 0]
    if not treated or not control:
        raise ValueError("both treatment groups must be present")

    mean_treated = sum(treated) / len(treated)
    mean_control = sum(control) / len(control)
    var_treated = sum((v - mean_treated) ** 2 for v in treated) / max(1, len(treated) - 1)
    var_control = sum((v - mean_control) ** 2 for v in control) / max(1, len(control) - 1)
    pooled = ((var_treated + var_control) / 2) ** 0.5
    return 0.0 if pooled == 0 else (mean_treated - mean_control) / pooled
