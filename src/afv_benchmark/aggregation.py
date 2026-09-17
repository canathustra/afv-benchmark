"""Explicit, descriptive AFV arithmetic; this module does not select EEG."""
from __future__ import annotations

import math
import numbers

import numpy as np


def _frequencies(values, name):
    array = np.asarray(values, dtype=object)
    if array.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional sequence")
    result = []
    for value in array:
        if value is None:
            result.append(float("nan"))
            continue
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, numbers.Real):
            raise ValueError(f"{name} must contain positive real frequencies or None/NaN")
        value = float(value)
        if math.isinf(value) or (math.isfinite(value) and value <= 0):
            raise ValueError(f"{name} must contain positive real frequencies or None/NaN")
        result.append(value)
    return np.asarray(result, dtype=float)


def summarize_afv(left_hz, right_hz, *, eligible, min_windows=2):
    """Sample SD of per-window bilateral means on explicitly eligible pairs.

    `eligible` is a required boolean mask supplied by the caller. It is not
    inferred from frequencies or method agreement. A pair is retained only when
    this mask is true and both channel frequencies are finite. None and NaN are
    missing, never zero. Infinity, nonpositive frequencies and nonnumeric values
    are invalid. `min_windows` controls arithmetic support only, not clinical
    validity, independent duration or a mandatory 90-second rule.

    The ordering is mean(left, right) per retained window, then sample SD
    (ddof=1) across those means. This can conceal opposed channel changes.
    """
    left = _frequencies(left_hz, "left_hz")
    right = _frequencies(right_hz, "right_hz")
    if left.shape != right.shape:
        raise ValueError("left_hz and right_hz must have the same length")
    mask = np.asarray(eligible)
    if mask.ndim == 1 and mask.size == 0:
        mask = mask.astype(bool)
    if mask.ndim != 1 or mask.shape != left.shape or mask.dtype.kind != "b":
        raise ValueError("eligible must be a boolean mask with one value per window")
    if isinstance(min_windows, (bool, np.bool_)) or not isinstance(min_windows, numbers.Integral) or min_windows < 2:
        raise ValueError("min_windows must be an integer >= 2")
    finite_pair = np.isfinite(left) & np.isfinite(right)
    retained = mask & finite_pair
    means = [float(l / 2 + r / 2) if keep else None
             for l, r, keep in zip(left, right, retained)]
    kept_means = np.asarray([value for value in means if value is not None], dtype=float)
    enough = len(kept_means) >= min_windows
    afv = float(np.std(kept_means, ddof=1)) if enough else None
    if afv is not None and not math.isfinite(afv):
        raise ValueError("frequencies are too large for a finite sample standard deviation")
    reasons = [
        "caller_ineligible" if not allowed else
        "missing_both_channels" if not (math.isfinite(l) or math.isfinite(r)) else
        "missing_left_channel" if not math.isfinite(l) else
        "missing_right_channel" if not math.isfinite(r) else "retained"
        for l, r, allowed in zip(left, right, mask)
    ]
    return {
        "afv_hz": afv, "computed": enough,
        "reason": "computed_from_retained_bilateral_means" if enough else "insufficient_retained_windows",
        "definition": "sample_sd_of_per_window_bilateral_mean", "ddof": 1,
        "min_windows": int(min_windows), "n_windows": len(left),
        "n_caller_eligible": int(np.count_nonzero(mask)),
        "n_jointly_finite": int(np.count_nonzero(finite_pair)),
        "n_retained": int(np.count_nonzero(retained)),
        "n_caller_ineligible": int(np.count_nonzero(~mask)),
        "n_eligible_missing_pair": int(np.count_nonzero(mask & ~finite_pair)),
        "eligible_mask": mask.tolist(), "jointly_finite_mask": finite_pair.tolist(),
        "retained_mask": retained.tolist(),
        "retained_indices": np.flatnonzero(retained).tolist(),
        "window_reasons": reasons, "bilateral_mean_hz": means,
        "independent_duration_seconds": None,
        "physiological_eligibility": "caller_supplied_not_validated",
    }
