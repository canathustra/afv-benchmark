import json

import numpy as np
import pytest

from afv_benchmark.demo import demo_payload, main, write_demo
from afv_benchmark.synthetic import generate_examples


def test_generation_is_deterministic_and_local():
    np.random.seed(111)
    state = np.random.get_state()
    first = generate_examples(17)
    second = generate_examples(17)
    after = np.random.get_state()
    assert state[0] == after[0]
    np.testing.assert_array_equal(state[1], after[1])
    assert state[2:] == after[2:]
    assert len(first) == 5
    for left, right in zip(first, second):
        np.testing.assert_array_equal(left.signals, right.signals)
        assert left.signals.shape == (5, 2, 2000)
        assert not left.signals.flags.writeable
    assert not np.array_equal(first[2].signals, generate_examples(18)[2].signals)


@pytest.mark.parametrize("seed", [-1, 1.5, True, "1"])
def test_invalid_seed(seed):
    with pytest.raises(ValueError):
        generate_examples(seed)


def test_smoke_examples_do_not_make_noise_or_competition_eligible():
    summary, rows = demo_payload(17)
    examples = {item["name"]: item for item in summary["examples"]}
    assert len(rows) == 5 * 5 * 2 * 3
    for name in ("noise_only", "competing_peaks"):
        for method in examples[name]["methods"].values():
            assert method["afv_hz"] is None
            assert method["n_caller_eligible"] == 0
        assert examples[name]["carrier_sequence_arithmetic"] is None
    assert examples["bilateral_opposed_change"]["carrier_sequence_arithmetic"]["afv_hz"] == 0.
    json.dumps([summary, rows], allow_nan=False)


def test_output_is_reproducible_and_refuses_overwrite(tmp_path):
    one = write_demo(tmp_path / "one", 17)
    two = write_demo(tmp_path / "two", 17)
    for filename in ("summary.json", "window_results.csv"):
        assert (one / filename).read_bytes() == (two / filename).read_bytes()
    with pytest.raises(FileExistsError):
        write_demo(one, 17)
    assert len(json.loads((one / "summary.json").read_text(encoding="utf-8"))["window_results"]) == 150


def test_cli(tmp_path, capsys):
    assert main(["--output", str(tmp_path / "demo"), "--seed", "17"]) == 0
    assert "software smoke" in capsys.readouterr().out
