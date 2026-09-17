"""Synthetic-only software demonstration; no scientific ranking or final method."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import platform

import numpy as np
import scipy

from . import __version__
from .aggregation import summarize_afv
from .estimators import METHODS, estimate_window, method_settings
from .synthetic import generate_examples


def demo_payload(seed=20260917):
    """Return a strict-JSON summary and flat rows without reading external data."""
    examples = generate_examples(seed)
    summary = {
        "schema_version": "1.0", "package_version": __version__, "seed": int(seed),
        "purpose": "software_smoke_examples_not_scientific_experiment_or_method_ranking",
        "data": "synthetic_only_no_recordings_or_patient_metadata",
        "limitations": [
            "Returned spectral candidates do not demonstrate biological alpha presence.",
            "Eligibility masks are supplied from the illustration design, not inferred from estimated frequencies.",
            "Each window is independently synthesized; no continuous duration or clinical validity is claimed.",
            "These examples do not select a final estimator or establish performance superiority.",
        ],
        "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "settings": method_settings(), "examples": [],
    }
    rows = []
    for example in examples:
        estimates = [[estimate_window(channel) for channel in window] for window in example.signals]
        entry = {"name": example.name, "description": example.description,
                 "eligibility_reason": example.eligibility_reason,
                 "carrier_frequencies_hz": {"left": example.left_carrier_hz, "right": example.right_carrier_hz},
                 "methods": {}}
        for method in METHODS:
            left = [window[0][method]["frequency_hz"] for window in estimates]
            right = [window[1][method]["frequency_hz"] for window in estimates]
            entry["methods"][method] = summarize_afv(left, right, eligible=example.eligible)
        entry["carrier_sequence_arithmetic"] = (
            summarize_afv(example.left_carrier_hz, example.right_carrier_hz, eligible=example.eligible)
            if example.left_carrier_hz is not None else None
        )
        for window_index, window in enumerate(estimates):
            for channel_index, channel in enumerate(window):
                for method, result in channel.items():
                    rows.append({"example": example.name, "window_index": window_index,
                                 "channel": ("left", "right")[channel_index], "method": method,
                                 "caller_eligible": example.eligible[window_index], **result})
        summary["examples"].append(entry)
    return summary, rows


def write_demo(output, seed=20260917):
    """Write two files into a new directory; refuse to overwrite existing output."""
    destination = Path(output)
    if destination.exists():
        raise FileExistsError("output directory already exists; choose a new directory")
    summary, rows = demo_payload(seed)
    summary["window_results"] = rows
    json_text = json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "summary.json").write_text(json_text, encoding="utf-8", newline="\n")
    fields = ["example", "window_index", "channel", "method", "caller_eligible", "frequency_hz",
              "returned", "reason", "n_peaks", "candidates_json", "diagnostics_json",
              "physiological_alpha_validity"]
    with (destination / "window_results.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            flat = {key: value for key, value in row.items() if key not in {"candidates", "diagnostics"}}
            flat["candidates_json"] = json.dumps(row["candidates"], allow_nan=False, separators=(",", ":"))
            flat["diagnostics_json"] = json.dumps(row["diagnostics"], allow_nan=False, separators=(",", ":"))
            writer.writerow(flat)
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="demo-output", help="new directory for synthetic demo outputs")
    parser.add_argument("--seed", type=int, default=20260917, help="nonnegative deterministic seed")
    args = parser.parse_args(argv)
    try:
        destination = write_demo(args.output, args.seed)
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    print(f"Wrote synthetic software smoke examples to {destination}")
    print("Files: summary.json and window_results.csv. No clinical validation or method ranking.")
    return 0
