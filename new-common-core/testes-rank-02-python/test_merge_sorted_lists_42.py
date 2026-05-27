#!/usr/bin/env python3
"""
42-style hidden tester for merge_sorted_lists.

Usage:
    python3 test_merge_sorted_lists_42.py merge_sorted_lists.py

Subject:
    Write a function:
        def merge_sorted_lists(nums1: list[int], nums2: list[int]) -> list[int]

Function-only rule:
    Because the subject asks for a FUNCTION, the submitted file must not execute
    anything at top level.

Allowed:
    - imports
    - constants
    - helper functions
    - the required merge_sorted_lists function

Rejected:
    - main()
    - print(...) at top level
    - input(...) at top level
    - calls at top level
    - if __name__ == "__main__"
    - any import-time output

Behavior tested:
    Return a NEW list containing all elements from nums1 and nums2 in sorted order.

Important:
    The implementation does not need to be identical to the reference.
    Any equivalent implementation passes.
"""

import ast
import importlib.util
import io
import os
import random
import sys
from contextlib import redirect_stdout


REQUIRED_FUNCTION = "merge_sorted_lists"


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


def reference(nums1, nums2):
    return sorted(nums1 + nums2)


def assert_case(fn, nums1, nums2, expected, name):
    original_nums1 = list(nums1)
    original_nums2 = list(nums2)

    try:
        got = fn(nums1, nums2)
    except Exception as exc:
        fail(
            f"{name}: function raised {type(exc).__name__}: {exc}\n"
            f"Input: nums1={original_nums1!r}, nums2={original_nums2!r}"
        )

    if type(got) is not list:
        fail(
            f"{name}: function must return a list, got {type(got).__name__}\n"
            f"Input: nums1={original_nums1!r}, nums2={original_nums2!r}\n"
            f"Returned: {got!r}"
        )

    if got != expected:
        fail(
            f"{name}: wrong result\n"
            f"Input:    nums1={original_nums1!r}, nums2={original_nums2!r}\n"
            f"Expected: {expected!r}\n"
            f"Got:      {got!r}"
        )

    if nums1 != original_nums1:
        fail(
            f"{name}: function mutated nums1\n"
            f"Before: {original_nums1!r}\n"
            f"After:  {nums1!r}"
        )

    if nums2 != original_nums2:
        fail(
            f"{name}: function mutated nums2\n"
            f"Before: {original_nums2!r}\n"
            f"After:  {nums2!r}"
        )

    if got is nums1 or got is nums2:
        fail(
            f"{name}: function returned one of the original input lists. "
            "Return a new merged list instead."
        )


def run_tests(path):
    fn = load_function(path)

    cases = [
        # Subject examples
        ("subject example 1", [1, 3, 5], [2, 4, 6], [1, 2, 3, 4, 5, 6]),
        ("subject example 2 duplicates", [1, 2, 4], [1, 3, 4], [1, 1, 2, 3, 4, 4]),
        ("subject example 3 first empty", [], [0], [0]),

        # Empty/minimal inputs
        ("both empty", [], [], []),
        ("second empty", [1], [], [1]),
        ("first empty multiple", [], [-2, 0, 5], [-2, 0, 5]),
        ("single elements ordered", [1], [2], [1, 2]),
        ("single elements reversed", [2], [1], [1, 2]),
        ("single elements equal", [7], [7], [7, 7]),

        # Negatives and zero
        ("negative numbers", [-5, -3, -1], [-4, -2, 0], [-5, -4, -3, -2, -1, 0]),
        ("mixed negative positive", [-10, 0, 10], [-5, 5], [-10, -5, 0, 5, 10]),
        ("all zeros", [0, 0], [0, 0, 0], [0, 0, 0, 0, 0]),

        # Duplicates must be preserved
        ("duplicates across lists", [1, 1, 2, 2], [1, 2, 2, 3], [1, 1, 1, 2, 2, 2, 2, 3]),
        ("many same values", [5, 5, 5], [5, 5], [5, 5, 5, 5, 5]),
        ("duplicates at boundaries", [1, 2, 2], [2, 2, 3], [1, 2, 2, 2, 2, 3]),

        # Different lengths
        ("first much longer", [1, 2, 3, 4, 5, 6], [7], [1, 2, 3, 4, 5, 6, 7]),
        ("second much longer", [10], [-5, -4, -3, -2, -1], [-5, -4, -3, -2, -1, 10]),
        ("interleaved different lengths", [1, 4, 7, 10], [2, 3, 5, 6, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),

        # Inputs already sorted but combined order is not just concatenation
        ("not just concatenation", [1, 100], [2, 3, 4], [1, 2, 3, 4, 100]),
        ("all nums2 before nums1", [10, 20], [1, 2, 3], [1, 2, 3, 10, 20]),

        # Large-ish deterministic cases
        ("large disjoint ranges", list(range(0, 200, 2)), list(range(1, 200, 2)), list(range(200))),
        ("large negative positive ranges", list(range(-100, 0)), list(range(0, 100)), list(range(-100, 100))),
    ]

    passed = 0

    for name, nums1, nums2, expected in cases:
        assert_case(fn, list(nums1), list(nums2), expected, name)
        passed += 1

    rng = random.Random(42)

    # Random sorted input lists against reference.
    for i in range(250):
        size1 = rng.randint(0, 120)
        size2 = rng.randint(0, 120)

        nums1 = sorted(rng.randint(-500, 500) for _ in range(size1))
        nums2 = sorted(rng.randint(-500, 500) for _ in range(size2))

        expected = reference(nums1, nums2)
        assert_case(fn, list(nums1), list(nums2), expected, f"random sorted case #{i + 1}")
        passed += 1

    # Pattern-heavy tests: catch hardcoded examples, lost duplicates, and mutation.
    patterns = [
        ([], []),
        ([1, 1, 1], [1, 1]),
        ([-3, -1, 2], [-2, 0, 3]),
        ([0, 10, 20], [5, 15, 25]),
        (list(range(-50, 51, 10)), list(range(-45, 56, 10))),
    ]

    for i, (nums1, nums2) in enumerate(patterns, start=1):
        for repeat in (1, 2, 5):
            expanded1 = sorted(nums1 * repeat)
            expanded2 = sorted(nums2 * repeat)
            expected = reference(expanded1, expanded2)
            assert_case(fn, list(expanded1), list(expanded2), expected, f"pattern case #{i}, repeat {repeat}")
            passed += 1

    print(f"OK: {passed} tests passed")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_merge_sorted_lists_42.py merge_sorted_lists.py", file=sys.stderr)
        sys.exit(2)

    try:
        run_tests(sys.argv[1])
    except AssertionError as exc:
        print(f"KO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
