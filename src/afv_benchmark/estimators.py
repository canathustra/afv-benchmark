"""Three fixed exploratory candidates for one 10-second, 200-Hz signal.

The local Savitzky-Golay (SG) variants are not official restingIAF replicas.
Input is already prepared by the caller; no filtering or re-referencing occurs.
Frequency selection alone does not establish physiological alpha measurability.
"""
from __future__ import annotations

import copy
import math
import warnings

import numpy as np
from scipy.signal import find_peaks, peak_prominences, savgol_filter, welch

FS = 200
N_SAMPLES = 2000
METHODS = ("welch_argmax", "sg_local_5p3", "sg_local_11p5")

_SG_COMMON = {
    "input": "raw_linear_Welch_PSD", "smooth_support": "full_PSD_0_100_Hz",
    "sg_mode": "interp", "detection_support_hz": [6., 15.],
    "center_band_hz_inclusive": [8., 13.], "prominence_db_min": 3.,
    "prominence_wlen_bins": 17, "prominence_domain": "10log10_smoothed_linear_PSD",
    "log_floor_relative_to_max_positive_smoothed_PSD": 1e-15,
    "interpolation": "3_bin_parabola_on_linear_smoothed_PSD_max_abs_offset_0.5_bin",
    "selection": "highest_smoothed_linear_PSD_at_native_peak_then_lowest_frequency",
    "multiple_peaks": "diagnose_and_select_not_automatic_rejection",
    "equal_strength": "exact_equality_no_tolerance_lowest_frequency_tie_break",
    "temporal_smoothing": False, "official_restingIAF_replica": False,
}
_SETTINGS = {
    "sampling_frequency_hz": FS, "samples": N_SAMPLES,
    "input": "caller_prepared_real_finite_signal_with_consistent_amplitude_units",
    "preprocessing_inside": False,
    "threshold_status": "exploratory_not_clinical_acceptance",
    "welch_common": {"window": "hann_periodic", "nperseg": 800, "noverlap": 400,
                     "nfft": 800, "detrend": "linear", "scaling": "density",
                     "average": "mean", "return_onesided": True, "grid_hz": .25},
    "welch_argmax": {"band_hz_inclusive": [8., 13.], "interpolation": False,
                     "positive_maximum_required": True, "tie_break": "first_lowest_bin"},
    "sg_local_5p3": {**_SG_COMMON, "window_length_bins": 5, "polyorder": 3},
    "sg_local_11p5": {**_SG_COMMON, "window_length_bins": 11, "polyorder": 5},
}


def method_settings():
    """Return a JSON-safe copy of the fixed numerical settings."""
    return copy.deepcopy(_SETTINGS)


def _json_value(value):
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [_json_value(v) for v in value]
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(value) else None
    return value


def _result(frequency=None, reason="no_peak", n_peaks=None, **extra):
    frequency = None if frequency is None else float(frequency)
    if frequency is not None and not math.isfinite(frequency):
        raise ValueError("Nonfinite frequency cannot be returned")
    return _json_value({"frequency_hz": frequency, "returned": frequency is not None,
                        "reason": reason, "n_peaks": n_peaks, "extra": extra})


def _sg(frequencies, power, window_length, polyorder):
    smooth = savgol_filter(power, window_length, polyorder, mode="interp")
    positive = smooth[smooth > 0]
    if not len(positive):
        return _result(reason="no_positive_smoothed_power", n_peaks=0)
    floor = max(float(np.max(positive)) * 1e-15, np.finfo(float).tiny)
    support = np.flatnonzero((frequencies >= 6.) & (frequencies <= 15.))
    log_power = 10. * np.log10(np.maximum(smooth[support], floor))
    # Detect on linear PSD; log floor cannot create a candidate maximum.
    local_peaks = find_peaks(smooth[support])[0]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        prominences = peak_prominences(log_power, local_peaks, wlen=17)[0]
    candidates = []
    for local_idx, prominence in zip(local_peaks, prominences):
        idx = int(support[local_idx])
        if smooth[idx] <= 0 or not np.isfinite(prominence) or prominence < 3.:
            continue
        left, center, right = smooth[idx - 1:idx + 2]
        curvature = left - 2. * center + right
        offset = .5 * (left - right) / curvature if curvature < 0 else 0.
        offset = float(np.clip(offset, -.5, .5))
        center_hz = float(frequencies[idx] + offset * (frequencies[1] - frequencies[0]))
        if 8. <= center_hz <= 13.:
            candidates.append({"frequency_hz": center_hz, "native_frequency_hz": float(frequencies[idx]),
                               "strength_linear": float(center), "prominence_db": float(prominence),
                               "interpolation_offset_bins": offset})
    candidates.sort(key=lambda row: (-row["strength_linear"], row["frequency_hz"]))
    extra = {"candidates": candidates, "multiple_peaks": len(candidates) > 1,
             "smoothed_nonpositive_bin_count": int(np.count_nonzero(smooth <= 0)),
             "log_floor": floor, "prominence_warnings": [str(w.message) for w in caught],
             "tie_count_at_selected_strength": sum(c["strength_linear"] == candidates[0]["strength_linear"] for c in candidates) if candidates else 0}
    if not candidates:
        return _result(reason="no_alpha_peak_with_3db_local_prominence", n_peaks=0, **extra)
    return _result(candidates[0]["frequency_hz"], "dominant_of_multiple_peaks" if len(candidates) > 1 else "ok",
                   len(candidates), **extra)


def _welch_argmax(frequencies, power):
    band = (frequencies >= 8.) & (frequencies <= 13.)
    band_power = power[band]
    maximum = float(np.max(band_power))
    frequency = float(frequencies[band][int(np.argmax(band_power))]) if maximum > 0 else None
    support = np.flatnonzero((frequencies >= 6.) & (frequencies <= 15.))
    peaks = support[find_peaks(power[support])[0]]
    native_peaks = peaks[(frequencies[peaks] >= 8.) & (frequencies[peaks] <= 13.)]
    candidates = [
        {"frequency_hz": float(frequencies[index]), "strength_linear": float(power[index]),
         "source": "native_local_maximum"}
        for index in native_peaks
    ]
    # A band-edge argmax need not be a local maximum on the wider 6-15 Hz support.
    if frequency is not None and not any(c["frequency_hz"] == frequency for c in candidates):
        candidates.append({"frequency_hz": frequency, "strength_linear": maximum,
                           "source": "band_argmax_without_native_local_maximum"})
    candidates.sort(key=lambda row: (-row["strength_linear"], row["frequency_hz"]))
    return _result(frequency, "ok" if frequency is not None else "nonpositive_alpha_psd",
                   len(native_peaks), candidates=candidates,
                   exact_max_count=int(np.count_nonzero(band_power == maximum)),
                   band_edge=frequency in (8., 13.),
                   candidate_semantics="selected_band_argmax_plus_native_local_maxima",
                   n_peaks_semantics="native_local_maxima_in_8_13_using_6_15_support")


def _public_result(result):
    diagnostics = result.pop("extra")
    result["candidates"] = diagnostics.pop("candidates", [])
    result["diagnostics"] = diagnostics
    result["physiological_alpha_validity"] = "not_assessed"
    return result


def estimate_window(x):
    """Return all three candidates for exactly 2,000 real finite samples.

    Input is one channel at 200 Hz, prepared by the caller. Invalid inputs raise
    ValueError. Algorithmic absence is frequency_hz=None and returned=False.
    The candidates list is method-specific spectral evidence, not distinct
    biological generators. A returned candidate does not establish eligibility.
    """
    array = np.asarray(x)
    if array.ndim != 1 or array.shape != (N_SAMPLES,) or array.dtype.kind not in "fiu":
        raise ValueError("x must be a real numeric 1D array of exactly 2000 samples")
    array = np.asarray(array, dtype=float)
    if not np.isfinite(array).all():
        raise ValueError("x must contain only finite samples")
    try:
        with np.errstate(over="raise", invalid="raise"):
            frequencies, power = welch(
                array, fs=FS, window="hann", nperseg=800, noverlap=400,
                nfft=800, detrend="linear", scaling="density", average="mean",
                return_onesided=True,
            )
    except FloatingPointError as exc:
        raise ValueError("signal magnitude cannot produce a finite power spectrum") from exc
    if not np.isfinite(power).all():
        raise ValueError("signal magnitude cannot produce a finite power spectrum")
    results = {
        "welch_argmax": _welch_argmax(frequencies, power),
        "sg_local_5p3": _sg(frequencies, power, 5, 3),
        "sg_local_11p5": _sg(frequencies, power, 11, 5),
    }
    return {method: _public_result(result) for method, result in results.items()}
