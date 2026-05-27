#!/usr/bin/env python3
"""
42-style hidden tester for mirror_matrix.

Usage:
    python3 test_mirror_matrix_42.py mirror_matrix.py

Subject:
    Write a function:
        def mirror_matrix(matrix: list[list]) -> list[list]

Function-only rule:
    Because the subject asks for a FUNCTION, the submitted file must not execute
    anything at top level.

Allowed:
    - imports
    - constants
    - helper functions
    - the required mirror_matrix function

Rejected:
    - main()
    - print(...) at top level
    - input(...) at top level
    - calls at top level
    - if __name__ == "__main__"
    - any import-time output

Behavior tested:
    Return a NEW matrix where each row is independently reversed.

Important:
    - The implementation does not need to be identical to the reference.
    - The input matrix and its inner rows must not be mutated.
    - The returned outer list must be new.
    - Each returned row must be a new list, not the original row object.
"""

import ast
import copy
import importlib.util
import io
import os
import random
import string
import sys
from contextlib import redirect_stdout


REQUIRED_FUNCTION = "mirror_matrix"


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


def reference(matrix):
    return [row[::-1] for row in matrix]


def assert_case(fn, matrix, expected, name):
    original = copy.deepcopy(matrix)
    original_row_ids = [id(row) for row in matrix]

    try:
        got = fn(matrix)
    except Exception as exc:
        fail(
            f"{name}: function raised {type(exc).__name__}: {exc}\n"
            f"Input: matrix={original!r}"
        )

    if type(got) is not list:
        fail(
            f"{name}: function must return a list, got {type(got).__name__}\n"
            f"Input: matrix={original!r}\n"
            f"Returned: {got!r}"
        )

    if got != expected:
        fail(
            f"{name}: wrong result\n"
            f"Input:    matrix={original!r}\n"
            f"Expected: {expected!r}\n"
            f"Got:      {got!r}"
        )

    if matrix != original:
        fail(
            f"{name}: function mutated the input matrix\n"
            f"Before: {original!r}\n"
            f"After:  {matrix!r}"
        )

    if got is matrix:
        fail(
            f"{name}: function returned the original matrix object. "
            "Return a new matrix instead."
        )

    if len(got) != len(matrix):
        fail(
            f"{name}: returned matrix has wrong number of rows\n"
            f"Expected rows: {len(matrix)}\n"
            f"Got rows:      {len(got)}"
        )

    for idx, row in enumerate(got):
        if type(row) is not list:
            fail(
                f"{name}: each returned row must be a list; row {idx} is {type(row).__name__}"
            )

        if idx < len(original_row_ids) and id(row) == original_row_ids[idx]:
            fail(
                f"{name}: returned row {idx} is the same object as the original row. "
                "Return new reversed rows instead."
            )


def run_tests(path):
    fn = load_function(path)

    cases = [
        # Subject examples
        (
            "subject example: square int matrix",
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            [[3, 2, 1], [6, 5, 4], [9, 8, 7]],
        ),
        (
            "subject example: strings",
            [["a", "b"], ["c", "d"]],
            [["b", "a"], ["d", "c"]],
        ),
        (
            "subject example: single element",
            [[42]],
            [[42]],
        ),
        (
            "subject example: empty matrix",
            [],
            [],
        ),

        # Empty/minimal rows
        ("one empty row", [[]], [[]]),
        ("multiple empty rows", [[], [], []], [[], [], []]),
        ("mixed empty and non-empty rows", [[1, 2], [], [3]], [[2, 1], [], [3]]),

        # Rectangular and ragged matrices
        (
            "rectangular matrix",
            [[1, 2, 3, 4], [5, 6, 7, 8]],
            [[4, 3, 2, 1], [8, 7, 6, 5]],
        ),
        (
            "ragged matrix",
            [[1], [2, 3], [4, 5, 6], []],
            [[1], [3, 2], [6, 5, 4], []],
        ),

        # Different value types
        (
            "mixed element types",
            [[1, "a", True], [None, 3.14, "x"]],
            [[True, "a", 1], ["x", 3.14, None]],
        ),
        (
            "nested objects as values",
            [[[1], [2], [3]], [{"a": 1}, {"b": 2}]],
            [[[3], [2], [1]], [{"b": 2}, {"a": 1}]],
        ),

        # Cases that catch column reversal/transposition mistakes
        (
            "not vertical mirror",
            [[1, 2], [3, 4], [5, 6]],
            [[2, 1], [4, 3], [6, 5]],
        ),
        (
            "not full flatten reverse",
            [[1, 2, 3], [4, 5, 6]],
            [[3, 2, 1], [6, 5, 4]],
        ),

        # Larger deterministic cases
        (
            "large rows",
            [list(range(100)), list(range(100, 200))],
            [list(reversed(range(100))), list(reversed(range(100, 200)))],
        ),
        (
            "many single rows",
            [[i] for i in range(50)],
            [[i] for i in range(50)],
        ),
    ]

    passed = 0

    for name, matrix, expected in cases:
        assert_case(fn, copy.deepcopy(matrix), expected, name)
        passed += 1

    rng = random.Random(42)

    # Random matrices with integers.
    for i in range(160):
        row_count = rng.randint(0, 40)
        matrix = []
        for _ in range(row_count):
            col_count = rng.randint(0, 30)
            row = [rng.randint(-500, 500) for _ in range(col_count)]
            matrix.append(row)

        expected = reference(matrix)
        assert_case(fn, copy.deepcopy(matrix), expected, f"random int matrix #{i + 1}")
        passed += 1

    # Random matrices with strings and mixed row sizes.
    alphabet = string.ascii_letters + string.digits + "!?"
    for i in range(120):
        row_count = rng.randint(0, 25)
        matrix = []
        for _ in range(row_count):
            col_count = rng.randint(0, 20)
            row = []
            for _ in range(col_count):
                length = rng.randint(0, 8)
                row.append("".join(rng.choice(alphabet) for _ in range(length)))
            matrix.append(row)

        expected = reference(matrix)
        assert_case(fn, copy.deepcopy(matrix), expected, f"random string matrix #{i + 1}")
        passed += 1

    # Pattern-heavy cases: catch hardcoded examples and wrong axis reversal.
    patterns = [
        [[1, 2, 3]],
        [[1], [2], [3]],
        [[1, 2], [3, 4]],
        [[1, 2, 3], [4], [], [5, 6]],
    ]

    for i, matrix in enumerate(patterns, start=1):
        for repeat in (1, 2, 5, 10):
            candidate = copy.deepcopy(matrix) * repeat
            expected = reference(candidate)
            assert_case(fn, copy.deepcopy(candidate), expected, f"pattern case #{i}, repeat {repeat}")
            passed += 1

    print(f"OK: {passed} tests passed")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_mirror_matrix_42.py mirror_matrix.py", file=sys.stderr)
        sys.exit(2)

    try:
        run_tests(sys.argv[1])
    except AssertionError as exc:
        print(f"KO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
