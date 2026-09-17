import json
import math

import numpy as np
import pytest

from afv_benchmark import summarize_afv


def test_sample_sd_of_bilateral_means():
    result = summarize_afv([8., 10., 12.], [12., 14., 16.], eligible=[True] * 3)
    assert result["bilateral_mean_hz"] == [10., 12., 14.]
    assert result["afv_hz"] == pytest.approx(2.)
    assert result["ddof"] == 1


def test_opposed_channel_changes_cancel_before_sd():
    result = summarize_afv([9., 10., 11.], [11., 10., 9.], eligible=[True] * 3)
    assert result["afv_hz"] == 0.
    assert result["computed"] is True
    assert np.std([9., 10., 11.], ddof=1) == 1.


def test_joint_support_and_caller_mask_are_explicit():
    result = summarize_afv([10., None, 11., 12., np.nan], [10., 11., np.nan, 14., 10.],
                           eligible=[True, True, True, False, True])
    assert result["retained_indices"] == [0]
    assert result["n_caller_eligible"] == 4
    assert result["n_jointly_finite"] == 2
    assert result["n_retained"] == 1
    assert result["n_eligible_missing_pair"] == 3
    assert result["n_caller_ineligible"] == 1
    assert result["window_reasons"] == ["retained", "missing_left_channel", "missing_right_channel",
                                         "caller_ineligible", "missing_left_channel"]
    assert result["bilateral_mean_hz"] == [10., None, None, None, None]
    assert result["afv_hz"] is None
    assert result["computed"] is False
    json.dumps(result, allow_nan=False)


def test_custom_minimum_is_arithmetic_support_only():
    result = summarize_afv([10., 11.], [10., 11.], eligible=[True, True], min_windows=3)
    assert result["n_retained"] == 2
    assert result["afv_hz"] is None
    assert result["independent_duration_seconds"] is None


def test_two_retained_windows_are_enough_for_sample_sd():
    result = summarize_afv([10., 11.], [10., 11.], eligible=[True, True])
    assert result["afv_hz"] == pytest.approx(math.sqrt(.5))


def test_empty_input_is_insufficient_not_zero():
    result = summarize_afv([], [], eligible=[])
    assert result["afv_hz"] is None
    assert result["n_retained"] == 0


def test_eligibility_argument_is_required():
    with pytest.raises(TypeError):
        summarize_afv([10., 10.], [10., 10.])


@pytest.mark.parametrize("eligible", [[1, 1], [True], [[True, True]], ["true", "true"]])
def test_invalid_masks(eligible):
    with pytest.raises(ValueError):
        summarize_afv([10., 11.], [10., 11.], eligible=eligible)


@pytest.mark.parametrize("minimum", [0, 1, 2., True, "2"])
def test_invalid_minimum(minimum):
    with pytest.raises(ValueError):
        summarize_afv([10., 11.], [10., 11.], eligible=[True, True], min_windows=minimum)


@pytest.mark.parametrize("bad", [np.inf, -np.inf, 0., -1., True, "10", 10 + 1j])
def test_invalid_frequencies(bad):
    with pytest.raises(ValueError):
        summarize_afv([10., bad], [10., 11.], eligible=[True, True])


def test_mismatched_channels():
    with pytest.raises(ValueError):
        summarize_afv([10.], [10., 11.], eligible=[True])
