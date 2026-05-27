#!/usr/bin/env python3
"""
42-style hidden tester for count_consecutive_digit_pairs.

Usage:
    python3 test_count_consecutive_digit_pairs_42.py count_consecutive_digit_pairs.py

Subject:
    Write a function:
        def count_consecutive_digit_pairs(s: str) -> int

Function-only rule:
    Because the subject asks for a FUNCTION, the submitted file must not execute
    anything at top level.

Allowed:
    - imports
    - constants
    - helper functions
    - the required count_consecutive_digit_pairs function

Rejected:
    - main()
    - print(...) at top level
    - input(...) at top level
    - calls at top level
    - if __name__ == "__main__"
    - any import-time output

Behavior tested:
    Count adjacent digit pairs where the second character is exactly the next
    digit/character after the first.

Important:
    The subject says "distinct consecutive digit pairs", but the provided
    correct implementation counts occurrences, not unique pair types.

    Example:
        "1212" -> 2
    because both adjacent "12" occurrences are counted.
"""

import ast
import importlib.util
import io
import os
import random
import string
import sys
from contextlib import redirect_stdout


REQUIRED_FUNCTION = "count_consecutive_digit_pairs"


def fail(message):
    raise AssertionError(message)


def check_function_only_file(path):
    if not os.path.exists(path):
        fail(f"File not found: {path}")

    source = open(path, "r", encoding="utf-8").read()

    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as exc:
        fail(f"SyntaxError: {exc}")

    found_required_function = False

    allowed_top_level = (
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.Import,
        ast.ImportFrom,
        ast.Assign,
        ast.AnnAssign,
        ast.Pass,
    )

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if node.name == REQUIRED_FUNCTION:
                found_required_function = True
            if node.name == "main":
                fail(
                    "This subject asks for a function only. "
                    "Do not submit a main() function."
                )

        if isinstance(node, ast.If):
            fail(
                "This subject asks for a function only. "
                "Do not include top-level if/main execution."
            )

        if isinstance(node, ast.Expr):
            fail(
                "This subject asks for a function only. "
                "Do not include top-level calls, prints, or expressions."
            )

        if isinstance(node, ast.Try):
            fail(
                "This subject asks for a function only. "
                "Do not include top-level execution blocks."
            )

        if not isinstance(node, allowed_top_level):
            fail(
                "This subject asks for a function only. "
                f"Invalid top-level statement: {type(node).__name__}"
            )

    if not found_required_function:
        fail(f"Function {REQUIRED_FUNCTION} was not found")


def load_function(path):
    check_function_only_file(path)

    spec = importlib.util.spec_from_file_location("candidate_module", path)
    module = importlib.util.module_from_spec(spec)

    captured_stdout = io.StringIO()

    try:
        with redirect_stdout(captured_stdout):
            spec.loader.exec_module(module)
    except Exception as exc:
        fail(f"Your file crashes when imported: {type(exc).__name__}: {exc}")

    if captured_stdout.getvalue() != "":
        fail(
            "This subject asks for a function only. "
            "Your file prints output at import time."
        )

    if not hasattr(module, REQUIRED_FUNCTION):
        fail(f"Function {REQUIRED_FUNCTION} was not found")

    fn = getattr(module, REQUIRED_FUNCTION)

    if not callable(fn):
        fail(f"{REQUIRED_FUNCTION} exists but is not callable")

    return fn


def reference(s):
    count = 0
    for i in range(len(s) - 1):
        if ord(s[i + 1]) == ord(s[i]) + 1:
            count += 1
    return count


def assert_case(fn, s, expected, name):
    try:
        got = fn(s)
    except Exception as exc:
        fail(
            f"{name}: function raised {type(exc).__name__}: {exc}\n"
            f"Input: s={s!r}"
        )

    if type(got) is not int:
        fail(
            f"{name}: function must return an int, got {type(got).__name__}\n"
            f"Input: s={s!r}\n"
            f"Returned: {got!r}"
        )

    if got != expected:
        fail(
            f"{name}: wrong result\n"
            f"Input:    s={s!r}\n"
            f"Expected: {expected}\n"
            f"Got:      {got}"
        )


def run_tests(path):
    fn = load_function(path)

    cases = [
        # Subject examples
        ("subject example: repeated groups", "1112233335", 2),
        ("subject example: full increasing chain", "1234", 3),
        ("subject example: no increasing pairs", "1111", 0),

        # Empty/minimal inputs
        ("empty string", "", 0),
        ("single digit zero", "0", 0),
        ("single digit nine", "9", 0),
        ("two digits valid low", "01", 1),
        ("two digits valid high", "89", 1),
        ("two digits invalid equal", "11", 0),
        ("two digits invalid descending", "21", 0),
        ("no wrap 90", "90", 0),

        # Count occurrences, not distinct pair types
        ("repeated same valid pair counted twice", "1212", 2),
        ("repeated same valid pair counted many times", "12121212", 4),
        ("many repeated 12 blocks", "1212121212", 5),
        ("distinct wording ambiguity check", "123123", 4),

        # Overlapping adjacent pairs
        ("overlapping chain 012", "012", 2),
        ("overlapping chain 34567", "34567", 4),
        ("full digit chain", "0123456789", 9),
        ("full digit chain repeated", "0123456789" * 3, 27),

        # Mixed valid and invalid adjacent pairs
        ("rise fall rise", "121", 1),
        ("alternating 120", "120120120", 5),
        ("valid pairs separated by invalids", "1122334455", 4),
        ("descending all", "9876543210", 0),
        ("almost descending with one rise", "987656", 1),
        ("zeros and ones", "000111", 1),
        ("long same digit", "7" * 200, 0),

        # Cases that catch set/dedup solutions
        ("same pair many occurrences", "0101010101", 5),
        ("two pair types repeated", "12123123", 5),

        # Cases that catch solutions checking numeric difference after int conversion
        # For digit-only strings this is equivalent, but these protect exact adjacency.
        ("all pairs valid except 9 to 0", "7890123", 5),
        ("many 89 no 90 wrap", "898989", 3),
    ]

    passed = 0

    for name, s, expected in cases:
        assert_case(fn, s, expected, name)
        passed += 1

    # Deterministic random digit-only tests.
    # The subject says the string consists of numeric digits, so these are the
    # required random tests.
    rng = random.Random(42)

    for i in range(250):
        length = rng.randint(0, 300)
        s = "".join(rng.choice(string.digits) for _ in range(length))
        expected = reference(s)
        assert_case(fn, s, expected, f"random digit-only case #{i + 1}")
        passed += 1

    # Deterministic pattern-heavy tests that catch off-by-one and hardcoded logic.
    patterns = [
        "0123456789",
        "9876543210",
        "00112233445566778899",
        "121212121212",
        "909090909090",
        "123450123450",
    ]

    for i, pattern in enumerate(patterns, start=1):
        for repeat in (1, 2, 5, 10, 25):
            s = pattern * repeat
            expected = reference(s)
            assert_case(fn, s, expected, f"pattern case #{i}, repeat {repeat}")
            passed += 1

    print(f"OK: {passed} tests passed")


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python3 test_count_consecutive_digit_pairs_42.py "
            "count_consecutive_digit_pairs.py",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        run_tests(sys.argv[1])
    except AssertionError as exc:
        print(f"KO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
