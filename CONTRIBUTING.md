# Contributing

This is early research software. Useful contributions include reproducible bug
reports, numerical tests, clearer documentation, and carefully scoped adapters.

Please include the package and dependency versions, the expected behavior, the
observed behavior, and a small synthetic reproduction. Do not upload patient
recordings, identifiers, or confidential research documents.

Before proposing a numerical change:

1. State which mathematical quantity or failure mode it changes.
2. Preserve the original comparison behavior or clearly version the change.
3. Test constant and changing known frequency, missing results, and competing
   peaks as applicable.
4. Report retained support together with error. Lower AFV alone is not success.
5. Distinguish passing software tests from physiological validation.

Run `python -m pytest` before submitting changes. Public contribution workflows
will be available if and when the maintainer publishes this candidate repository.
