# Provenance and attribution

## Selected source lineage

The initial public candidate is extracted from a project-local exploratory
benchmark prepared on 13 September 2026. It deliberately includes only three
frequency adapters; it does not reproduce the complete historical pipeline,
its datasets, its full benchmark, or subsequent multi-method comparisons.

| Internal source identifier | SHA-256 at extraction | Selected use |
|---|---|---|
| `estimators.py` | `1276e6cc809fd44b670eecd349705b40f853626425962ed2e38544413272f5de` | Local SG candidate calculation and exploratory settings |
| `feature_extractor.py` | `531c1edd402e0ff1d6ebabf36a216391aa362b61b484c5e0b3c25d8540023a5b` | Positive-power Welch maximum selection contract |
| `peak_measurability.py` | `6453b430f727cfea1a87eab44316214f2b3a45ba9dab8355b7d01e14fcda3f4d` | Explicit parameters of the project-local SciPy Welch wrapper |

These identifiers document provenance; the package has no runtime dependency on
those private source files. Their other functions are not part of this release.
The source files' hashes identify the bounded extraction point and do not assert
authorship, legal clearance, or biological validity.

## Adaptation boundaries

The local SG arithmetic retains the original smoothing, detection support,
prominence, interpolation, ranking and tie rules. Packaging introduces a small
portable API, explicit input validation and public documentation. The Welch
adapter calls SciPy directly with the preserved explicit spectrum settings;
no dynamically loaded private modules are required.

The bilateral SD helper, command-line demonstration, packaging and software tests
are release infrastructure. They are not a new final scientific method. The
synthetic examples are software illustrations, not the original full experimental
panel. They do not inherit a claim of validation from the wider research project.

## Scientific attribution

Corcoran AW, Alday PM, Schlesewsky M, Bornkessel-Schlesewsky I. Toward a reliable,
automated method of individual alpha frequency (IAF) quantification.
Psychophysiology. 2018;55:e13064.
[https://doi.org/10.1111/psyp.13064](https://doi.org/10.1111/psyp.13064).

The local SG adapters are inspired by this area of work. They are not the
authors' restingIAF software and do not implement its complete preprocessing,
derivative, channel-decision and summary pipeline. No restingIAF source is
included or relicensed by this package.

The numerical implementation uses:

- [NumPy](https://numpy.org/), under its own BSD-3-Clause license.
- [SciPy](https://scipy.org/), under its own BSD-3-Clause license.
- SciPy's documented [Welch](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html),
  [Savitzky–Golay](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html),
  local-peak and prominence routines.

Dependencies are installed separately, not vendored. Their licenses and
attribution requirements remain applicable to those dependencies. The proposed
MIT license covers the project package, not independent third-party projects.

## Reproducibility boundary

Software tests and numerical parity checks are intended to establish the
behavior of this extracted core. They cannot establish that an EEG segment
contains a physiological alpha rhythm, that a retained window is clinically
appropriate, or that a particular estimator should be selected for a study.
