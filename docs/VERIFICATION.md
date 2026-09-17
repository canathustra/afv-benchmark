# Verification scope

Local checks on 17 September 2026 passed all 48 tests in both of these Windows
environments:

| Python | NumPy | SciPy | Result |
|---|---|---|---|
| 3.12.10 | 2.4.4 | 1.18.0 | 48 tests passed |
| 3.12.10 | 2.5.3 | 1.18.1 | Fresh environment: 48 tests passed |

The tests cover frequency input validation, the fixed spectrum settings,
candidate reporting, missing paired results, explicit eligibility, bilateral
arithmetic, deterministic synthetic outputs, and refusal to overwrite an
existing demo directory. They are bounded checks of software behavior.

An independent check compared the three methods against functions extracted
from their immediate historical sources on 18 newly constructed synthetic cases
(54 method/input comparisons). It covered zero signals, off-grid tones, band
edges, noise, weak tones, and competing peaks. The local SG function's parsed
numerical body was identical to its source. Numerical parity preserves inherited behavior; it
does not establish that the inherited estimator measures the desired biological
rhythm. See [provenance](PROVENANCE.md).

The repository includes a Linux continuous-integration configuration for Python
3.10, 3.12, and 3.13. Results for individual released commits are available in
[GitHub Actions](https://github.com/canathustra/afv-benchmark/actions/workflows/tests.yml).
The table above records the local pre-release checks. The declared dependency
range is broader than those environments; compatibility with every allowed
combination is not established.

No patient recordings are required for these checks. No clinical accuracy,
physiological alpha-validity threshold, population generalization, or scientific
method ranking is established by passing them.
