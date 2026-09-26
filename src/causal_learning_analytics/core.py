# Calculation reading guide: ../CALCULATIONS.md (repository root).
# Weighted contrast = sum(wT·Y)/sum(wT) - sum(wC·Y)/sum(wC).
# Treated weights are 1/e and control weights 1/(1-e), where e is estimated exposure propensity. Effective sample size is (sum w)^2/sum(w^2). ATE-style weighting does not itself identify a causal effect; overlap weighting changes the target population.

import math
import random
from collections.abc import Mapping, Sequence
from numbers import Real


def _as_finite_numbers(values: Sequence[Real], name: str) -> list[float]:
    values = list(values)
    if not values:
        raise ValueError(f"{name} must not be empty")
    result = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(f"{name} must contain only numeric values")
        value = float(value)
        if not math.isfinite(value):
            raise ValueError(f"{name} must contain only finite values")
        result.append(value)
    return result


def _validate_treatment(treatment: Sequence[int]) -> list[int]:
    treatment = list(treatment)
    if not treatment:
        raise ValueError("treatment must not be empty")
    for value in treatment:
        if isinstance(value, bool) or value not in (0, 1):
            raise ValueError("treatment must contain integer 0 and 1 only")
    if 0 not in treatment or 1 not in treatment:
        raise ValueError("both treatment groups must be present")
    return treatment


def _validate_propensity(propensity: Sequence[Real]) -> list[float]:
    propensity = _as_finite_numbers(propensity, "propensity")
    if any(value < 0.0 or value > 1.0 for value in propensity):
        raise ValueError("propensity scores must be between 0 and 1")
    return propensity


def _validate_inputs(
    treatment: Sequence[int],
    outcome: Sequence[Real],
    propensity: Sequence[Real],
) -> tuple[list[int], list[float], list[float]]:
    treatment = _validate_treatment(treatment)
    outcome = _as_finite_numbers(outcome, "outcome")
    propensity = _validate_propensity(propensity)

    if not (len(treatment) == len(outcome) == len(propensity)):
        raise ValueError("treatment, outcome, and propensity must have equal length")

    return treatment, outcome, propensity


def _clip_scores(
    propensity: Sequence[float],
    clip: float | None,
) -> tuple[list[float], int]:
    propensity = list(propensity)

    if clip is None:
        if any(value <= 0.0 or value >= 1.0 for value in propensity):
            raise ValueError(
                "propensity scores at 0 or 1 violate positivity; "
                "provide an explicit clip value only if that sensitivity choice is justified"
            )
        return propensity, 0

    if isinstance(clip, bool) or not isinstance(clip, Real):
        raise ValueError("clip must be numeric or None")
    clip = float(clip)
    if not 0.0 < clip < 0.5:
        raise ValueError("clip must be between 0 and 0.5")

    clipped = [
        min(1.0 - clip, max(clip, value))
        for value in propensity
    ]
    clipped_count = sum(
        original != adjusted
        for original, adjusted in zip(propensity, clipped)
    )
    return clipped, clipped_count


def ipw_weights(
    treatment: Sequence[int],
    propensity: Sequence[Real],
    *,
    clip: float | None = None,
) -> dict:
    """Return ATE inverse-probability weights and clipping diagnostics."""
    treatment = _validate_treatment(treatment)
    propensity = _validate_propensity(propensity)

    if len(treatment) != len(propensity):
        raise ValueError("treatment and propensity must have equal length")

    scores, clipped_count = _clip_scores(propensity, clip)
    weights = [
        1.0 / score if flag == 1 else 1.0 / (1.0 - score)
        for flag, score in zip(treatment, scores)
    ]

    return {
        "weights": weights,
        "propensity_used": scores,
        "clip": clip,
        "clipped_count": clipped_count,
    }


def raw_mean_difference(
    treatment: Sequence[int],
    outcome: Sequence[Real],
) -> float:
    """Return the unadjusted treated-minus-control outcome mean difference."""
    treatment = _validate_treatment(treatment)
    outcome = _as_finite_numbers(outcome, "outcome")
    if len(treatment) != len(outcome):
        raise ValueError("treatment and outcome must have equal length")

    treated = [
        value
        for flag, value in zip(treatment, outcome)
        if flag == 1
    ]
    control = [
        value
        for flag, value in zip(treatment, outcome)
        if flag == 0
    ]
    return sum(treated) / len(treated) - sum(control) / len(control)


def ipw_ate(
    treatment: Sequence[int],
    outcome: Sequence[Real],
    propensity: Sequence[Real],
    *,
    clip: float | None = None,
    normalized: bool = False,
) -> float:
    """Estimate the ATE using Horvitz-Thompson or normalized (Hajek) IPW."""
    treatment, outcome, propensity = _validate_inputs(
        treatment,
        outcome,
        propensity,
    )
    weight_info = ipw_weights(treatment, propensity, clip=clip)
    weights = weight_info["weights"]

    treated_weighted = [
        weight * value
        for flag, weight, value in zip(treatment, weights, outcome)
        if flag == 1
    ]
    control_weighted = [
        weight * value
        for flag, weight, value in zip(treatment, weights, outcome)
        if flag == 0
    ]

    if normalized:
        treated_weights = [
            weight
            for flag, weight in zip(treatment, weights)
            if flag == 1
        ]
        control_weights = [
            weight
            for flag, weight in zip(treatment, weights)
            if flag == 0
        ]
        return (
            sum(treated_weighted) / sum(treated_weights)
            - sum(control_weighted) / sum(control_weights)
        )

    sample_size = len(treatment)
    return (
        sum(treated_weighted) / sample_size
        - sum(control_weighted) / sample_size
    )



def _solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Solve a small dense linear system with partial-pivot Gaussian elimination."""
    size = len(vector)
    augmented = [
        [float(value) for value in row] + [float(vector[index])]
        for index, row in enumerate(matrix)
    ]

    for column in range(size):
        pivot = max(
            range(column, size),
            key=lambda row: abs(augmented[row][column]),
        )
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("propensity model system is singular")
        augmented[column], augmented[pivot] = (
            augmented[pivot],
            augmented[column],
        )

        pivot_value = augmented[column][column]
        augmented[column] = [
            value / pivot_value
            for value in augmented[column]
        ]

        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor == 0:
                continue
            augmented[row] = [
                current - factor * pivot_current
                for current, pivot_current in zip(
                    augmented[row],
                    augmented[column],
                )
            ]

    return [augmented[row][-1] for row in range(size)]


def _sigmoid(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exp_value = math.exp(value)
    return exp_value / (1.0 + exp_value)


def fit_propensity_logistic(
    treatment: Sequence[int],
    covariates: Mapping[str, Sequence[Real]],
    *,
    l2: float = 1e-6,
    max_iterations: int = 100,
    tolerance: float = 1e-8,
) -> dict:
    """Fit a transparent logistic propensity baseline on pre-treatment covariates.

    Continuous covariates are standardized internally. This small dependency-free
    implementation is intended for reproducible demonstrations and benchmarking,
    not as a substitute for a mature statistical package in production research.
    """
    treatment = _validate_treatment(treatment)
    if not isinstance(covariates, Mapping) or not covariates:
        raise ValueError("covariates must be a non-empty mapping")
    if isinstance(l2, bool) or not isinstance(l2, Real) or l2 < 0:
        raise ValueError("l2 must be a non-negative number")
    if (
        isinstance(max_iterations, bool)
        or not isinstance(max_iterations, int)
        or max_iterations <= 0
    ):
        raise ValueError("max_iterations must be a positive integer")
    if (
        isinstance(tolerance, bool)
        or not isinstance(tolerance, Real)
        or tolerance <= 0
    ):
        raise ValueError("tolerance must be positive")

    names = []
    columns = []
    means = {}
    scales = {}

    for name, raw_values in covariates.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("covariate names must be non-empty strings")
        values = _as_finite_numbers(raw_values, name)
        if len(values) != len(treatment):
            raise ValueError(
                f"covariate {name} must match treatment length"
            )
        column_mean = sum(values) / len(values)
        variance = sum(
            (value - column_mean) ** 2
            for value in values
        ) / len(values)
        scale = math.sqrt(variance)
        if math.isclose(scale, 0.0, abs_tol=1e-12):
            raise ValueError(
                f"covariate {name} has zero variance and cannot identify a logistic slope"
            )
        names.append(name)
        means[name] = column_mean
        scales[name] = scale
        columns.append(
            [
                (value - column_mean) / scale
                for value in values
            ]
        )

    design = []
    for row_index in range(len(treatment)):
        design.append(
            [1.0]
            + [
                column[row_index]
                for column in columns
            ]
        )

    coefficient_count = len(names) + 1
    coefficients = [0.0] * coefficient_count
    converged = False
    completed_iterations = 0

    for iteration in range(1, max_iterations + 1):
        linear_predictor = [
            sum(
                coefficient * feature
                for coefficient, feature in zip(
                    coefficients,
                    row,
                )
            )
            for row in design
        ]
        probabilities = [
            min(1.0 - 1e-12, max(1e-12, _sigmoid(value)))
            for value in linear_predictor
        ]

        gradient = [0.0] * coefficient_count
        information = [
            [0.0] * coefficient_count
            for _ in range(coefficient_count)
        ]

        for row, flag, probability in zip(
            design,
            treatment,
            probabilities,
        ):
            residual = flag - probability
            variance_weight = probability * (1.0 - probability)

            for j in range(coefficient_count):
                gradient[j] += row[j] * residual
                for k in range(coefficient_count):
                    information[j][k] += (
                        variance_weight * row[j] * row[k]
                    )

        for index in range(1, coefficient_count):
            gradient[index] -= float(l2) * coefficients[index]
            information[index][index] += float(l2)

        step = _solve_linear_system(information, gradient)
        coefficients = [
            coefficient + delta
            for coefficient, delta in zip(coefficients, step)
        ]
        completed_iterations = iteration

        if max(abs(delta) for delta in step) < float(tolerance):
            converged = True
            break

    final_scores = []
    for row in design:
        linear_value = sum(
            coefficient * feature
            for coefficient, feature in zip(
                coefficients,
                row,
            )
        )
        final_scores.append(
            min(1.0 - 1e-12, max(1e-12, _sigmoid(linear_value)))
        )

    return {
        "scores": final_scores,
        "converged": converged,
        "iterations": completed_iterations,
        "intercept": coefficients[0],
        "standardized_coefficients": {
            name: coefficient
            for name, coefficient in zip(
                names,
                coefficients[1:],
            )
        },
        "covariate_means": means,
        "covariate_scales": scales,
        "l2": float(l2),
    }

def common_support(
    treatment: Sequence[int],
    propensity: Sequence[Real],
) -> dict:
    """Summarize empirical treated/control propensity-score common support."""
    treatment = _validate_treatment(treatment)
    propensity = _validate_propensity(propensity)
    if len(treatment) != len(propensity):
        raise ValueError("treatment and propensity must have equal length")

    treated_scores = [
        score
        for flag, score in zip(treatment, propensity)
        if flag == 1
    ]
    control_scores = [
        score
        for flag, score in zip(treatment, propensity)
        if flag == 0
    ]

    treated_range = (min(treated_scores), max(treated_scores))
    control_range = (min(control_scores), max(control_scores))
    lower = max(treated_range[0], control_range[0])
    upper = min(treated_range[1], control_range[1])
    has_support = lower <= upper

    def fraction_inside(scores):
        if not has_support:
            return 0.0
        return sum(lower <= score <= upper for score in scores) / len(scores)

    treated_fraction = fraction_inside(treated_scores)
    control_fraction = fraction_inside(control_scores)

    return {
        "treated_range": treated_range,
        "control_range": control_range,
        "common_support": (lower, upper) if has_support else None,
        "treated_fraction_in_support": treated_fraction,
        "control_fraction_in_support": control_fraction,
        "overall_fraction_in_support": (
            (
                sum(
                    has_support and lower <= score <= upper
                    for score in propensity
                )
                / len(propensity)
            )
            if has_support
            else 0.0
        ),
    }


def overlap_fraction(
    treatment: Sequence[int],
    propensity: Sequence[Real],
) -> float:
    """Return the share of all observations inside empirical common support."""
    return common_support(treatment, propensity)["overall_fraction_in_support"]


def _group_mean(
    treatment: Sequence[int],
    values: Sequence[float],
    group: int,
    weights: Sequence[float] | None = None,
) -> float:
    selected = [
        (value, 1.0 if weights is None else weight)
        for flag, value, weight in zip(
            treatment,
            values,
            weights if weights is not None else [1.0] * len(values),
        )
        if flag == group
    ]
    numerator = sum(value * weight for value, weight in selected)
    denominator = sum(weight for _, weight in selected)
    if denominator <= 0:
        raise ValueError("group weights must sum to a positive value")
    return numerator / denominator


def _group_variance(
    treatment: Sequence[int],
    values: Sequence[float],
    group: int,
    weights: Sequence[float] | None = None,
) -> float | None:
    selected_values = [
        value
        for flag, value in zip(treatment, values)
        if flag == group
    ]
    if len(selected_values) < 2:
        return None

    if weights is None:
        group_mean = sum(selected_values) / len(selected_values)
        return (
            sum((value - group_mean) ** 2 for value in selected_values)
            / (len(selected_values) - 1)
        )

    selected = [
        (value, weight)
        for flag, value, weight in zip(treatment, values, weights)
        if flag == group
    ]
    weight_sum = sum(weight for _, weight in selected)
    weight_sq_sum = sum(weight * weight for _, weight in selected)
    denominator = weight_sum - weight_sq_sum / weight_sum
    if denominator <= 0:
        return None

    group_mean = sum(value * weight for value, weight in selected) / weight_sum
    return (
        sum(
            weight * (value - group_mean) ** 2
            for value, weight in selected
        )
        / denominator
    )


def standardized_mean_difference(
    treatment: Sequence[int],
    values: Sequence[Real],
    *,
    weights: Sequence[Real] | None = None,
) -> float | None:
    """Return treated-minus-control SMD, or None when scale is not estimable."""
    treatment = _validate_treatment(treatment)
    values = _as_finite_numbers(values, "values")
    if len(treatment) != len(values):
        raise ValueError("treatment and values must have equal length")

    numeric_weights = None
    if weights is not None:
        numeric_weights = _as_finite_numbers(weights, "weights")
        if len(numeric_weights) != len(values):
            raise ValueError("weights and values must have equal length")
        if any(weight <= 0 for weight in numeric_weights):
            raise ValueError("weights must be positive")

    mean_treated = _group_mean(
        treatment,
        values,
        1,
        numeric_weights,
    )
    mean_control = _group_mean(
        treatment,
        values,
        0,
        numeric_weights,
    )
    var_treated = _group_variance(
        treatment,
        values,
        1,
        numeric_weights,
    )
    var_control = _group_variance(
        treatment,
        values,
        0,
        numeric_weights,
    )

    if var_treated is None or var_control is None:
        return None

    pooled_variance = (var_treated + var_control) / 2.0
    if math.isclose(pooled_variance, 0.0, abs_tol=1e-12):
        return None

    return (
        mean_treated - mean_control
    ) / math.sqrt(pooled_variance)


def covariate_balance(
    treatment: Sequence[int],
    covariates: Mapping[str, Sequence[Real]],
    *,
    weights: Sequence[Real] | None = None,
) -> dict:
    """Return group means and SMDs for named pre-treatment covariates."""
    treatment = _validate_treatment(treatment)
    if not isinstance(covariates, Mapping) or not covariates:
        raise ValueError("covariates must be a non-empty mapping")

    numeric_weights = None
    if weights is not None:
        numeric_weights = _as_finite_numbers(weights, "weights")
        if len(numeric_weights) != len(treatment):
            raise ValueError("weights must match treatment length")
        if any(weight <= 0 for weight in numeric_weights):
            raise ValueError("weights must be positive")

    result = {}
    for name, values in covariates.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("covariate names must be non-empty strings")
        values = _as_finite_numbers(values, name)
        if len(values) != len(treatment):
            raise ValueError(
                f"covariate {name} must match treatment length"
            )
        result[name] = {
            "treated_mean": _group_mean(
                treatment,
                values,
                1,
                numeric_weights,
            ),
            "control_mean": _group_mean(
                treatment,
                values,
                0,
                numeric_weights,
            ),
            "smd": standardized_mean_difference(
                treatment,
                values,
                weights=numeric_weights,
            ),
        }
    return result


def effective_sample_size(weights: Sequence[Real]) -> float:
    """Return Kish effective sample size for positive analysis weights."""
    weights = _as_finite_numbers(weights, "weights")
    if any(weight <= 0 for weight in weights):
        raise ValueError("weights must be positive")
    return sum(weights) ** 2 / sum(weight * weight for weight in weights)


def weight_diagnostics(
    treatment: Sequence[int],
    weights: Sequence[Real],
) -> dict:
    """Summarize ATE weight magnitude and effective sample size."""
    treatment = _validate_treatment(treatment)
    weights = _as_finite_numbers(weights, "weights")
    if len(treatment) != len(weights):
        raise ValueError("treatment and weights must have equal length")
    if any(weight <= 0 for weight in weights):
        raise ValueError("weights must be positive")

    treated_weights = [
        weight
        for flag, weight in zip(treatment, weights)
        if flag == 1
    ]
    control_weights = [
        weight
        for flag, weight in zip(treatment, weights)
        if flag == 0
    ]

    return {
        "min_weight": min(weights),
        "max_weight": max(weights),
        "mean_weight": sum(weights) / len(weights),
        "overall_ess": effective_sample_size(weights),
        "treated_ess": effective_sample_size(treated_weights),
        "control_ess": effective_sample_size(control_weights),
    }


def _percentile(sorted_values: Sequence[float], probability: float) -> float:
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be between 0 and 1")
    if len(sorted_values) == 1:
        return sorted_values[0]

    position = probability * (len(sorted_values) - 1)
    lower_index = int(math.floor(position))
    upper_index = int(math.ceil(position))
    if lower_index == upper_index:
        return sorted_values[lower_index]

    weight = position - lower_index
    return (
        sorted_values[lower_index] * (1 - weight)
        + sorted_values[upper_index] * weight
    )


def bootstrap_ipw_ci(
    treatment: Sequence[int],
    outcome: Sequence[Real],
    propensity: Sequence[Real],
    *,
    clip: float | None = None,
    normalized: bool = True,
    confidence: float = 0.95,
    iterations: int = 2000,
    seed: int = 42,
) -> tuple[float, float]:
    """Percentile bootstrap CI conditional on the supplied propensity scores."""
    treatment, outcome, propensity = _validate_inputs(
        treatment,
        outcome,
        propensity,
    )
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be between 0 and 1")
    if isinstance(iterations, bool) or not isinstance(iterations, int):
        raise ValueError("iterations must be an integer")
    if iterations < 200:
        raise ValueError("iterations must be at least 200")

    rng = random.Random(seed)
    estimates = []
    sample_size = len(treatment)

    for _ in range(iterations):
        indices = [
            rng.randrange(sample_size)
            for _ in range(sample_size)
        ]
        sampled_treatment = [treatment[index] for index in indices]
        if 0 not in sampled_treatment or 1 not in sampled_treatment:
            continue
        sampled_outcome = [outcome[index] for index in indices]
        sampled_propensity = [propensity[index] for index in indices]
        estimates.append(
            ipw_ate(
                sampled_treatment,
                sampled_outcome,
                sampled_propensity,
                clip=clip,
                normalized=normalized,
            )
        )

    minimum_valid = max(100, iterations // 2)
    if len(estimates) < minimum_valid:
        raise ValueError(
            "too few valid bootstrap resamples contained both treatment groups"
        )

    estimates.sort()
    alpha = 1.0 - confidence
    return (
        _percentile(estimates, alpha / 2.0),
        _percentile(estimates, 1.0 - alpha / 2.0),
    )



def clipping_sensitivity(
    treatment: Sequence[int],
    outcome: Sequence[Real],
    propensity: Sequence[Real],
    *,
    clips: Sequence[float | None] = (None, 0.01, 0.025, 0.05, 0.10),
) -> list[dict]:
    """Compare ATE estimates and weight stability across clipping choices."""
    treatment, outcome, propensity = _validate_inputs(
        treatment,
        outcome,
        propensity,
    )
    clips = list(clips)
    if not clips:
        raise ValueError("clips must not be empty")

    results = []
    for clip in clips:
        try:
            weight_info = ipw_weights(
                treatment,
                propensity,
                clip=clip,
            )
            diagnostics = weight_diagnostics(
                treatment,
                weight_info["weights"],
            )
            results.append(
                {
                    "clip": clip,
                    "status": "ok",
                    "clipped_count": weight_info["clipped_count"],
                    "ipw_ate_ht": ipw_ate(
                        treatment,
                        outcome,
                        propensity,
                        clip=clip,
                        normalized=False,
                    ),
                    "ipw_ate_hajek": ipw_ate(
                        treatment,
                        outcome,
                        propensity,
                        clip=clip,
                        normalized=True,
                    ),
                    "max_weight": diagnostics["max_weight"],
                    "overall_ess": diagnostics["overall_ess"],
                }
            )
        except ValueError as exc:
            results.append(
                {
                    "clip": clip,
                    "status": "not_estimable",
                    "reason": str(exc),
                }
            )

    return results

def causal_analysis_record(
    *,
    estimand: str = "ATE",
    treatment: str,
    outcome: str,
    covariates: Sequence[str],
    propensity_source: str,
    assumptions: Sequence[str] | None = None,
) -> dict:
    """Create a compact, serializable declaration of the causal analysis."""
    if estimand != "ATE":
        raise ValueError("the current implementation supports ATE only")

    text_fields = {
        "treatment": treatment,
        "outcome": outcome,
        "propensity_source": propensity_source,
    }
    for name, value in text_fields.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")

    covariates = list(covariates)
    if not covariates or any(
        not isinstance(value, str) or not value.strip()
        for value in covariates
    ):
        raise ValueError("covariates must contain non-empty strings")

    default_assumptions = [
        "consistency",
        "conditional exchangeability given measured pre-treatment covariates",
        "positivity",
        "no interference",
        "correct treatment and outcome measurement",
    ]

    supplied_assumptions = (
        default_assumptions
        if assumptions is None
        else list(assumptions)
    )
    if not supplied_assumptions or any(
        not isinstance(value, str) or not value.strip()
        for value in supplied_assumptions
    ):
        raise ValueError("assumptions must contain non-empty strings")

    return {
        "estimand": estimand,
        "treatment": treatment.strip(),
        "outcome": outcome.strip(),
        "covariates": [value.strip() for value in covariates],
        "propensity_source": propensity_source.strip(),
        "assumptions": [value.strip() for value in supplied_assumptions],
    }


def analyze_ipw(
    treatment: Sequence[int],
    outcome: Sequence[Real],
    propensity: Sequence[Real],
    *,
    covariates: Mapping[str, Sequence[Real]] | None = None,
    clip: float | None = None,
    confidence: float = 0.95,
    bootstrap_iterations: int = 2000,
    bootstrap_seed: int = 42,
    support_fraction_threshold: float = 0.80,
    balance_threshold: float = 0.10,
    ess_ratio_threshold: float = 0.50,
    max_weight_threshold: float = 10.0,
) -> dict:
    """Run a transparent ATE IPW baseline with diagnostics and review flags."""
    treatment, outcome, propensity = _validate_inputs(
        treatment,
        outcome,
        propensity,
    )

    for value, name in (
        (support_fraction_threshold, "support_fraction_threshold"),
        (balance_threshold, "balance_threshold"),
        (ess_ratio_threshold, "ess_ratio_threshold"),
        (max_weight_threshold, "max_weight_threshold"),
    ):
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(f"{name} must be numeric")

    if not 0.0 <= support_fraction_threshold <= 1.0:
        raise ValueError("support_fraction_threshold must be between 0 and 1")
    if balance_threshold < 0:
        raise ValueError("balance_threshold must be non-negative")
    if not 0.0 < ess_ratio_threshold <= 1.0:
        raise ValueError("ess_ratio_threshold must be in (0, 1]")
    if max_weight_threshold <= 0:
        raise ValueError("max_weight_threshold must be positive")

    weight_info = ipw_weights(
        treatment,
        propensity,
        clip=clip,
    )
    weights = weight_info["weights"]
    support = common_support(treatment, propensity)
    weight_summary = weight_diagnostics(treatment, weights)

    balance_before = None
    balance_after = None
    if covariates is not None:
        balance_before = covariate_balance(
            treatment,
            covariates,
        )
        balance_after = covariate_balance(
            treatment,
            covariates,
            weights=weights,
        )

    raw_difference = raw_mean_difference(treatment, outcome)
    ht_ate = ipw_ate(
        treatment,
        outcome,
        propensity,
        clip=clip,
        normalized=False,
    )
    hajek_ate = ipw_ate(
        treatment,
        outcome,
        propensity,
        clip=clip,
        normalized=True,
    )
    hajek_ci = bootstrap_ipw_ci(
        treatment,
        outcome,
        propensity,
        clip=clip,
        normalized=True,
        confidence=confidence,
        iterations=bootstrap_iterations,
        seed=bootstrap_seed,
    )

    treated_count = sum(treatment)
    control_count = len(treatment) - treated_count
    review_flags = ["causal_assumptions_unverified"]

    if min(treated_count, control_count) < 2:
        review_flags.append("small_group")

    if any(score <= 0.0 or score >= 1.0 for score in propensity):
        review_flags.append("positivity_violation")

    if weight_info["clipped_count"]:
        review_flags.append("propensity_clipping_used")

    if (
        support["common_support"] is None
        or support["treated_fraction_in_support"] < support_fraction_threshold
        or support["control_fraction_in_support"] < support_fraction_threshold
    ):
        review_flags.append("poor_common_support")

    if weight_summary["max_weight"] > max_weight_threshold:
        review_flags.append("extreme_weights")

    if (
        weight_summary["overall_ess"] / len(treatment)
        < ess_ratio_threshold
    ):
        review_flags.append("low_effective_sample_size")

    if balance_after is not None:
        any_not_estimable = any(
            diagnostic["smd"] is None
            for diagnostic in balance_after.values()
        )
        any_problem = any(
            diagnostic["smd"] is not None
            and abs(diagnostic["smd"]) > balance_threshold
            for diagnostic in balance_after.values()
        )
        if any_not_estimable:
            review_flags.append("post_weight_balance_not_estimable")
        if any_problem:
            review_flags.append("post_weight_balance_problem")

    return {
        "estimand": "ATE",
        "sample_size": len(treatment),
        "treated_count": treated_count,
        "control_count": control_count,
        "raw_mean_difference": raw_difference,
        "ipw_ate_ht": ht_ate,
        "ipw_ate_hajek": hajek_ate,
        "confidence_level": confidence,
        "hajek_ate_ci": hajek_ci,
        "propensity_original_range": (
            min(propensity),
            max(propensity),
        ),
        "propensity_used_range": (
            min(weight_info["propensity_used"]),
            max(weight_info["propensity_used"]),
        ),
        "clip": clip,
        "clipped_count": weight_info["clipped_count"],
        "common_support": support,
        "weight_diagnostics": weight_summary,
        "balance_before": balance_before,
        "balance_after": balance_after,
        "clipping_sensitivity": clipping_sensitivity(
            treatment,
            outcome,
            propensity,
        ),
        "analysis_flags": review_flags,
    }
