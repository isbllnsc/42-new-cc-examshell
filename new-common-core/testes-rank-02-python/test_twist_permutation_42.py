#!/usr/bin/env python3
"""
42-style hidden tester for twist_permutation.

Usage:
    python3 test_twist_permutation_42.py twist_permutation.py

Subject:
    Write a function:
        def twist_permutation(lst: list[int], n: int) -> list[int]

Function-only rule:
    Because the subject asks for a FUNCTION, the submitted file must not execute
    anything at top level.

Allowed:
    - imports
    - constants
    - helper functions
    - the required twist_permutation function

Rejected:
    - main()
    - print(...) at top level
    - input(...) at top level
    - calls at top level
    - if __name__ == "__main__"
    - any import-time output

Behavior tested:
    Return a NEW list where elements are rotated to the right by n positions.
    Rotation uses n % len(lst), matching the provided correct implementation.

Important:
    - The implementation does not need to be identical to the reference.
    - Any equivalent implementation passes.
    - The input list must not be mutated.
"""

import ast
import importlib.util
import io
import os
import random
import sys
from contextlib import redirect_stdout


REQUIRED_FUNCTION = "twist_permutation"


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


def reference(lst, n):
    n = n % len(lst)
    return lst[-n:] + lst[:-n]


def assert_case(fn, lst, n, expected, name):
    original = list(lst)

    try:
        got = fn(lst, n)
    except Exception as exc:
        fail(
            f"{name}: function raised {type(exc).__name__}: {exc}\n"
            f"Input: lst={original!r}, n={n!r}"
        )

    if type(got) is not list:
        fail(
            f"{name}: function must return a list, got {type(got).__name__}\n"
            f"Input: lst={original!r}, n={n!r}\n"
            f"Returned: {got!r}"
        )

    if got != expected:
        fail(
            f"{name}: wrong result\n"
            f"Input:    lst={original!r}, n={n!r}\n"
            f"Expected: {expected!r}\n"
            f"Got:      {got!r}"
        )

    if lst != original:
        fail(
            f"{name}: function mutated the input list\n"
            f"Before: {original!r}\n"
            f"After:  {lst!r}"
        )

    if got is lst:
        fail(
            f"{name}: function returned the original list object. "
            "Return a new rotated list instead."
        )


def run_tests(path):
    fn = load_function(path)

    cases = [
        # Subject examples
        ("subject example 1", [1, 2, 3, 4, 5], 2, [4, 5, 1, 2, 3]),
        ("subject example 2 modulo", [1, 2, 3], 4, [3, 1, 2]),
        ("subject example 3 zero shift", [10, 20, 30, 40], 0, [10, 20, 30, 40]),

        # Empty is intentionally not tested because the provided correct implementation
        # performs n % len(lst), so the defined behavior requires non-empty lists.

        # Minimal inputs
        ("single element n zero", [42], 0, [42]),
        ("single element n one", [42], 1, [42]),
        ("single element huge n", [42], 999, [42]),

        # Direction checks
        ("right by one", [1, 2, 3, 4], 1, [4, 1, 2, 3]),
        ("right by len minus one", [1, 2, 3, 4], 3, [2, 3, 4, 1]),
        ("not left rotation", [1, 2, 3, 4, 5], 1, [5, 1, 2, 3, 4]),

        # Modulo behavior
        ("n exactly list length", [7, 8, 9], 3, [7, 8, 9]),
        ("n multiple of length", [7, 8, 9], 300, [7, 8, 9]),
        ("n much larger than length", [1, 2, 3, 4, 5, 6], 20, [5, 6, 1, 2, 3, 4]),
        ("n huge prime-ish", [0, 1, 2, 3, 4, 5, 6], 1000003, [3, 4, 5, 6, 0, 1, 2]),

        # Two element edge cases
        ("two elements swap", [1, 2], 1, [2, 1]),
        ("two elements no-op modulo", [1, 2], 2, [1, 2]),
        ("two elements huge odd", [1, 2], 999, [2, 1]),

        # Values treated as opaque integers
        ("negative integers", [-1, -2, -3, -4], 2, [-3, -4, -1, -2]),
        ("duplicates preserved", [5, 5, 1, 5, 2], 2, [5, 2, 5, 5, 1]),
        ("zero values preserved", [0, 1, 0, 2, 0], 3, [0, 2, 0, 0, 1]),
        ("unsorted list", [9, 1, 8, 2, 7, 3], 4, [8, 2, 7, 3, 9, 1]),

        # Negative n support follows Python modulo behavior of provided implementation.
        ("negative n minus one", [1, 2, 3, 4, 5], -1, [2, 3, 4, 5, 1]),
        ("negative n larger", [1, 2, 3, 4, 5], -7, [3, 4, 5, 1, 2]),
        ("negative n multiple", [1, 2, 3], -6, [1, 2, 3]),
    ]

    passed = 0

    for name, lst, n, expected in cases:
        assert_case(fn, list(lst), n, expected, name)
        passed += 1

    rng = random.Random(42)

    # Deterministic random tests against reference behavior.
    for i in range(250):
        size = rng.randint(1, 120)
        lst = [rng.randint(-1000, 1000) for _ in range(size)]
        n = rng.randint(0, 5000)

        expected = reference(lst, n)
        assert_case(fn, list(lst), n, expected, f"random positive n case #{i + 1}")
        passed += 1

    # Negative n tests, because the reference handles them through modulo.
    for i in range(120):
        size = rng.randint(1, 80)
        lst = [rng.randint(-1000, 1000) for _ in range(size)]
        n = rng.randint(-5000, -1)

        expected = reference(lst, n)
        assert_case(fn, list(lst), n, expected, f"random negative n case #{i + 1}")
        passed += 1

    # Pattern-heavy cases: catch hardcoded examples, left-rotation, and off-by-one.
    patterns = [
        [1, 2, 3, 4, 5],
        [0, 0, 1, 1, 2, 2],
        [-3, -2, -1, 0, 1, 2, 3],
        list(range(20)),
        list(range(20, 0, -1)),
    ]

    for i, base in enumerate(patterns, start=1):
        for n in range(0, len(base) * 3 + 1):
            expected = reference(base, n)
            assert_case(fn, list(base), n, expected, f"pattern case #{i}, n={n}")
            passed += 1

    print(f"OK: {passed} tests passed")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_twist_permutation_42.py twist_permutation.py", file=sys.stderr)
        sys.exit(2)

    try:
        run_tests(sys.argv[1])
    except AssertionError as exc:
        print(f"KO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
