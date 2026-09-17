# Release scope and roadmap

## Initial candidate

This release packages a small existing exploratory numerical core for independent
inspection and reuse. Its runnable scope is Welch maximum, two local SG adapters,
bilateral SD arithmetic, and synthetic illustrations. It is not a release of the
entire research archive or the complete multi-method comparison program.

## Work proposed for later versions

1. Versioned adapters with clear distinctions between official upstream code,
   local implementations, and modified variants.
2. A broader reproducible synthetic benchmark with prespecified known-frequency,
   absent-rhythm, multiple-peak, amplitude, artifact, and support conditions.
3. Evaluation on each method's retained windows and on common retained windows,
   reporting both errors and retention.
4. A richer measurement contract retaining alternatives, method-specific support,
   errors, and unresolved physiological eligibility as separate fields.
5. Independent validation of a prespecified measurement workflow before any
   claim of clinical suitability or a preferred final estimator.

These are proposed development directions, not completed validation or a promise
that all methods will be included. Method changes require their own evidence and
versioning. No parameter should be optimized to maximize clinical group differences
or minimize AFV without regard to known truth and data retention.

## Release boundaries

No recording reader, clinical dataset, participant metadata, manuscript, clinical
group comparison, trained classifier, or final automatic eligibility rule is
included. Contributions should use distributable synthetic examples and keep
private clinical material outside issues, pull requests, and test fixtures.
