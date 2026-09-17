import json

import numpy as np
import pytest

from afv_benchmark import FS, METHODS, N_SAMPLES, estimate_window, method_settings


def tone(frequency):
    return np.sin(2 * np.pi * frequency * np.arange(N_SAMPLES) / FS)


@pytest.mark.parametrize("signal", [
    np.zeros(1999), np.zeros(2001), np.zeros((1, 2000)),
    np.full(2000, np.nan), np.full(2000, np.inf), np.ones(2000, dtype=complex),
    np.ones(2000, dtype=bool), ["0"] * 2000, [None] * 2000,
])
def test_invalid_signal_rejected(signal):
    with pytest.raises(ValueError):
        estimate_window(signal)


def test_zero_signal_is_absence_not_zero_frequency():
    results = estimate_window(np.zeros(N_SAMPLES))
    assert tuple(results) == METHODS
    for result in results.values():
        assert result["frequency_hz"] is None
        assert result["returned"] is False
        assert result["candidates"] == []
    json.dumps(results, allow_nan=False)


def test_on_grid_tone_and_json_contract():
    results = estimate_window(tone(10.))
    for result in results.values():
        assert result["frequency_hz"] == pytest.approx(10., abs=.01)
        assert result["returned"] is True
        assert result["physiological_alpha_validity"] == "not_assessed"
    json.dumps(results, allow_nan=False)


def test_argmax_keeps_quarter_hz_grid():
    result = estimate_window(tone(10.125))["welch_argmax"]
    assert result["frequency_hz"] in (10., 10.25)
    assert result["frequency_hz"] != 10.125


def test_competing_peaks_are_preserved_without_automatic_rejection():
    results = estimate_window(tone(9.) + tone(11.))
    for method in METHODS:
        result = results[method]
        candidates = [row["frequency_hz"] for row in result["candidates"]]
        assert any(abs(freq - 9.) < .02 for freq in candidates)
        assert any(abs(freq - 11.) < .02 for freq in candidates)
        assert result["returned"] is True
    assert results["sg_local_5p3"]["reason"] == "dominant_of_multiple_peaks"


def test_estimator_does_not_mutate_input():
    signal = tone(10.)
    original = signal.copy()
    estimate_window(signal)
    np.testing.assert_array_equal(signal, original)


def test_settings_copy_does_not_reconfigure_methods():
    settings = method_settings()
    settings["welch_common"]["nfft"] = 999
    assert method_settings()["welch_common"]["nfft"] == 800


def test_overflow_is_a_programming_error_not_missing_alpha():
    with pytest.raises(ValueError, match="finite power spectrum"):
        estimate_window(tone(10.) * 1e300)
