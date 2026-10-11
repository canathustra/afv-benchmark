# AFV Benchmark

Small, inspectable research tools for exploring alpha-frequency variability
(AFV) measurement and its failure modes.

**Status: early research software, version 0.1.0.** This package
contains three exploratory frequency estimators and synthetic demonstrations.
It does not provide a validated alpha detector, a clinical AFV standard, or a
recommended winning method.

## Why this exists

A frequency estimate can change because the signal changed, because a different
peak became dominant, or because the estimator responded to noise. AFV research
needs to keep those possibilities visible. A small variability value alone does
not establish accurate measurement.

This initial package makes a limited numerical core independently runnable:

- Welch maximum within 8–13 Hz (`welch_argmax`).
- Two local Savitzky–Golay peak adapters (`sg_local_5p3`, `sg_local_11p5`).
- Explicit candidate lists, missing results, and diagnostic reasons.
- A bilateral sample-SD helper with an explicit caller-supplied eligibility mask.
- Deterministic synthetic demonstrations and software tests.

The SG adapters are local exploratory implementations inspired by the IAF
literature. They are **not** the original restingIAF implementation. The wider
research project examines other methods; those are outside this release.

## Install and run

Use Python 3.10 or later. From a copy of this repository:

```sh
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m afv_benchmark --output demo-output
python -m pytest
```

Installation downloads the declared Python dependencies. Running the demo reads
no external recording and generates only artificial signals. Its JSON and CSV
outputs are numerical illustrations, not a scientific method ranking or clinical
validation study. See [methods and interpretation](docs/METHODS.md).

The demo creates `demo-output/summary.json` and
`demo-output/window_results.csv`. Choose a new output directory for each run;
the demo refuses to overwrite an existing directory.

## Use the numerical core

```python
import numpy as np
from afv_benchmark import estimate_window, summarize_afv

t = np.arange(2000) / 200.0
x = 20.0 * np.sin(2 * np.pi * 10.25 * t)
estimates = estimate_window(x)
print(estimates["welch_argmax"])

summary = summarize_afv(
    [9.0, 10.0, 11.0],
    [9.0, 10.0, 11.0],
    eligible=[True, True, True],
    min_windows=2,
)
print(summary)
```

See [the complete synthetic API example](examples/basic_usage.py) for another
example, including how opposing channel changes can cancel in the bilateral mean.

`estimate_window` expects one finite real 10-second channel at 200 Hz. For a real
research recording, appropriate preprocessing, channel/reference definition,
window selection, and evidence of physiological eligibility are the caller's
responsibility. This package performs no filtering, re-referencing, artifact
rejection, eye-state inference, or sleep scoring.

`summarize_afv` calculates the sample SD of the bilateral mean frequency across
jointly retained windows. It does not establish that those windows contain alpha,
meet a duration requirement, or represent independent observations. Missing
estimates stay missing. A mathematically valid zero SD is not evidence that alpha
was measurable.

## Scientific scope and reuse

- [Methods, assumptions, and limitations](docs/METHODS.md)
- [Provenance and source references](docs/PROVENANCE.md)
- [Roadmap and release boundaries](docs/ROADMAP.md)
- [Verification scope](docs/VERIFICATION.md)
- [Contributing](CONTRIBUTING.md)
- [Release history](CHANGELOG.md)
- [Initial 0.1.0 release manifest](https://github.com/canathustra/afv-benchmark/blob/a2cb224e2d769a32e0a941be8f3f9cc43823aa93/RELEASE_MANIFEST.json)

The release manifest records the original 0.1.0 contents and hashes.
It describes that release snapshot, rather than later documentation updates.

Only software and synthetic examples are included. No clinical recordings,
participant-level results, manuscript drafts, or private research documents are
distributed. Please use synthetic reproductions when reporting problems.

## Citation and license

See [CITATION.cff](CITATION.cff) for citation metadata. No journal publication or
software DOI is claimed for this release. Please identify the exact
version or commit used in your work, and cite the underlying methods when relevant.

This software is distributed under the [MIT license](LICENSE). Third-party
dependencies retain their own licenses. The public repository is
[canathustra/afv-benchmark](https://github.com/canathustra/afv-benchmark).

Development and packaging used AI coding assistance. Numerical code, software
checks, and scientific claims remain the maintainers' responsibility. Tests
establish bounded software behavior, not biological or clinical validity.

## Related projects

- [Clinical Neurology Portfolio](https://github.com/canathustra/clinical-neurology-portfolio): interactive teaching materials and the public educational archive.
- [NeuroEDX Lab](https://github.com/canathustra/neuroedx-lab): synthetic EMG/NCS teaching tools.

These are separate educational projects; their inclusion does not establish validation of AFV methods.
