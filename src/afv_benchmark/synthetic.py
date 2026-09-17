"""Deterministic software smoke inputs, not a research benchmark experiment."""
from __future__ import annotations

from dataclasses import dataclass
import numbers

import numpy as np

from .estimators import FS, N_SAMPLES


@dataclass(frozen=True)
class SmokeExample:
    """Arrays are windows x channels x samples; neither channel is patient data."""

    name: str
    description: str
    signals: np.ndarray
    eligible: tuple[bool, ...]
    left_carrier_hz: tuple[float, ...] | None
    right_carrier_hz: tuple[float, ...] | None
    eligibility_reason: str


def generate_examples(seed=20260917):
    """Generate five small cases with a local PCG64 RNG and no global RNG edits.

    Every 10-second window is synthesized separately. Adjacent array rows are
    not asserted to be a continuous recording. Noise-only and competing-peak
    examples have no single target frequency; their explicit demonstration
    eligibility is false even if a numerical candidate is returned.
    """
    if isinstance(seed, (bool, np.bool_)) or not isinstance(seed, numbers.Integral) or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    time = np.arange(N_SAMPLES, dtype=float) / FS
    cases = [
        ("constant_frequency", "Five independent windows with the same 10.125-Hz carrier.",
         (10.125,) * 5, (10.125,) * 5, "carrier_present_by_construction"),
        ("changing_frequency", "A simple carrier sequence across independent windows.",
         (9.5, 9.75, 10., 10.25, 10.5), (9.5, 9.75, 10., 10.25, 10.5),
         "carrier_present_by_construction"),
        ("noise_only", "Gaussian noise without an added oscillatory carrier; candidates may still be returned.",
         None, None, "no_added_carrier_single_frequency_target_undefined"),
        ("competing_peaks", "Two equal-amplitude carriers at 9 and 11 Hz; no unique frequency target is assigned.",
         None, None, "two_carriers_no_unique_frequency_target"),
        ("bilateral_opposed_change", "Opposed channel trajectories have a constant bilateral carrier mean.",
         (9., 9.5, 10., 10.5, 11.), (11., 10.5, 10., 9.5, 9.),
         "carriers_present_by_construction_bilateral_mean_can_cancel_change"),
    ]
    examples = []
    for case_index, (name, description, left, right, eligibility_reason) in enumerate(cases):
        rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([int(seed), case_index])))
        signals = np.empty((5, 2, N_SAMPLES), dtype=float)
        for window_index in range(5):
            for channel_index, carrier in enumerate((left, right)):
                phase = float(rng.uniform(0., 2. * np.pi))
                if name == "noise_only":
                    signal = rng.normal(0., 1., N_SAMPLES)
                elif name == "competing_peaks":
                    signal = (np.sin(2. * np.pi * 9. * time + phase)
                              + np.sin(2. * np.pi * 11. * time + phase / 2.))
                else:
                    signal = np.sin(2. * np.pi * carrier[window_index] * time + phase)
                    if name != "bilateral_opposed_change":
                        signal += rng.normal(0., .03, N_SAMPLES)
                signals[window_index, channel_index] = signal
        signals.setflags(write=False)
        examples.append(SmokeExample(name, description, signals, (left is not None,) * 5,
                                     left, right, eligibility_reason))
    return examples
