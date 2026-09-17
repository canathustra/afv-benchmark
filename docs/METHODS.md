# Methods and interpretation

## Input contract

The frequency API accepts exactly 2,000 finite real samples representing a
10-second channel at 200 Hz. The spectrum's units follow the input amplitude
unit squared per Hz. Examples use arbitrary synthetic amplitude units.

The initial internal adapters expected already re-referenced and filtered EEG
windows. This release exposes only the frequency step. It does not reproduce an
end-to-end historical recording pipeline. Supplying raw clinical EEG directly
does not make its returned frequencies physiologically eligible for AFV.

## Shared spectrum

The Welch calculation uses SciPy with explicitly set parameters:

| Parameter | Value |
|---|---|
| Sampling frequency | 200 Hz |
| Window | Periodic Hann |
| Segment length | 800 samples / 4 seconds |
| Segment overlap | 400 samples / 50% |
| FFT length | 800 samples |
| Detrending | Linear, within each Welch segment |
| Scaling and average | One-sided density, arithmetic mean |
| Native frequency spacing | 0.25 Hz |

The 10-second input window and 4-second Welch segments are different quantities.
Interpolating a peak does not create new independent spectral information.

## Three exploratory adapters

### Welch maximum

Select the largest positive PSD value in the inclusive 8–13 Hz band. Exact ties
use the lowest-frequency bin. Local maxima are reported as diagnostics, but are
not an acceptance gate. The selected maximum may lie at a band edge, and even
noise can produce a returned frequency. This method is a numerical baseline,
not a test for the presence of a physiological alpha rhythm.

### Local SG adapters

Apply Savitzky–Golay smoothing to the full linear PSD with either five bins and
polynomial order three, or eleven bins and polynomial order five. Use `interp`
edge handling. Find local maxima on the smoothed linear spectrum within 6–15 Hz.
Assess their prominence on the log-power spectrum using 17 bins and a minimum
of 3 dB. The logarithm floor is the maximum positive smoothed power times 1e-15,
bounded below by the smallest positive normal floating-point value.

Refine each candidate with a three-bin parabola on the smoothed linear PSD,
limiting the offset to half a native bin. Keep refined centers inside 8–13 Hz.
Order candidates by decreasing native smoothed peak power, then increasing
frequency. Preserve alternatives and diagnostic reasons. Multiple peaks do not
automatically cause rejection in these legacy exploratory adapters.

These settings are inherited exploratory choices. They are not validated
clinical thresholds, and this release does not claim to reproduce restingIAF.
The local method's selection and peak-validity rules differ from the published
method and its official code.

## AFV arithmetic

For retained window i, compute m_i = (f_left,i + f_right,i) / 2. The helper returns
the sample standard deviation of the m_i sequence (`ddof=1`), in Hz. This is not
the average of the two channel SDs.

The caller must explicitly provide a boolean eligibility mask. A window is
retained only when that mask is true and both frequencies are finite. Missing
values are not converted into zeros or imputed from the other channel. The
minimum number of windows is an arithmetic requirement chosen by the caller,
at least two; it is not a clinically justified duration threshold.

No time coordinates are supplied to this helper, so it cannot establish unique
recording duration, continuity, independence, overlap, or a 90-second support
rule. Opposing changes in the two channels can cancel in their mean; retain and
inspect channel-level results. Selected-window SD may change simply because the
set of retained windows changed.

## Synthetic illustrations

The demo contains constant frequency, changing frequency, noise-only, competing
peaks, and opposing bilateral changes. They are small deterministic software
examples. They do not reproduce the full historical benchmark, span realistic
EEG variability, establish a false-positive rate, or support a winner ranking.

Known synthetic construction is used only to label and interpret these examples.
It is not information available to the frequency estimators. Any synthetic
eligibility mask is explicitly supplied for demonstration and is not an automated
clinical eligibility decision.

## Missingness and validity

Invalid numerical input raises an error. A completed method may return no
frequency; that is represented explicitly rather than as zero Hz or AFV=0.
No returned frequency, multiple candidate peaks, and a numerical exception are
different conditions. None automatically proves biological alpha absence.

Software reproducibility and agreement between methods do not establish the
identity of the underlying rhythm. Independent physiological validation,
artifact and vigilance evidence, window selection, and generalization remain
separate research tasks. No clinical diagnostic or treatment use is established.

## References

- Welch PD. The use of fast Fourier transform for the estimation of power
  spectra: a method based on time averaging over short, modified periodograms.
  IEEE Transactions on Audio and Electroacoustics. 1967;15:70–73.
  See the [SciPy Welch documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html).
- Corcoran AW, Alday PM, Schlesewsky M, Bornkessel-Schlesewsky I. Toward a
  reliable, automated method of individual alpha frequency (IAF) quantification.
  Psychophysiology. 2018;55:e13064. [DOI](https://doi.org/10.1111/psyp.13064).
  Cited as methodological context, not as a validation of these local adapters.
- [SciPy Savitzky–Golay documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html).
