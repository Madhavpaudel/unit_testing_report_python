"""Shared helper for the staged test files (test_stage1_*.py ... test_stage4_*.py).
Keeps each stage file focused on one thing: printing PASS/FAIL lines and a
final tally, so screenshots stay clean and stage-specific.
"""

_passed = 0
_failed = 0


def check(name, condition):
    global _passed, _failed
    if condition:
        _passed += 1
        print(f"PASS {name}")
    else:
        _failed += 1
        print(f"FAIL {name}")


def summary():
    print(f"\n{_passed} passed, {_failed} failed")
    return _failed == 0


def reset():
    """Zero the counters - used when a single script runs more than one
    logical batch of tests (e.g. a 'before fix' batch and an 'after fix'
    batch) and each batch needs its own independent tally."""
    global _passed, _failed
    _passed = 0
    _failed = 0
