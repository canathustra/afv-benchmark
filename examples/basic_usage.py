"""Minimal synthetic API use after installing this package."""
import json

import numpy as np

from afv_benchmark import FS, N_SAMPLES, estimate_window, summarize_afv

signal = np.sin(2 * np.pi * 10.125 * np.arange(N_SAMPLES) / FS)
print(json.dumps(estimate_window(signal), indent=2, allow_nan=False))

# Illustrative arithmetic inputs; the caller explicitly supplies eligibility.
summary = summarize_afv([9., 10., 11., None], [11., 10., 9., 10.],
                        eligible=[True, True, True, True])
print(json.dumps(summary, indent=2, allow_nan=False))
# Opposed channel changes cancel here: the retained bilateral means are all 10 Hz.
