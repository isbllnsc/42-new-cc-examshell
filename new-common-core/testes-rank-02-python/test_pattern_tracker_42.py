#!/usr/bin/env python3
"""
42-style hidden tester for pattern_tracker.

Usage:
    python3 test_pattern_tracker_42.py pattern_tracker.py

Subject:
    Write a function:
        def pattern_tracker(string: str) -> int

Function-only rule:
    Because the subject asks for a FUNCTION, the submitted file must not execute
    anything at top level.

Allowed:
    - imports
    - constants
    - helper functions
    - the required pattern_tracker function

Rejected:
    - main()
    - print(...) at top level
    - input(...) at top level
    - calls at top level
    - if __name__ == "__main__"
    - any import-time output

Behavior tested:
    Count adjacent character pairs where both characters can be converted with int()
    and the second digit is exactly 1 greater than the first.

Important:
    The subject says non-numeric characters are ignored during comparison, but the
    provided correct implementation does NOT skip across non-numeric characters.
    It only counts truly adjacent numeric-character pairs.

    Therefore:
        "1234"   -> 3
        "a12b3"  -> 1
        "a1b2c3" -> 0

    The implementation does not need to be identical to the reference solution.
    Any equivalent implementation passes.
"""

import ast
import importlib.util
import io
import os
import random
import string
import sys
from contextlib import redirect_stdout


REQUIRED_FUNCTION = "pattern_tracker"


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


def reference(value):
    result = 0

    for i in range(len(value)):
        try:
            a = int(value[i + 1])
            b = int(value[i])
        except Exception:
            continue

        if a - b == 1:
            result += 1

    return result


def assert_case(fn, value, expected, name):
    try:
        got = fn(value)
    except Exception as exc:
        fail(
            f"{name}: function raised {type(exc).__name__}: {exc}\n"
            f"Input: string={value!r}"
        )

    if type(got) is not int:
        fail(
            f"{name}: function must return an int, got {type(got).__name__}\n"
            f"Input: string={value!r}\n"
            f"Returned: {got!r}"
        )

    if got != expected:
        fail(
            f"{name}: wrong result\n"
            f"Input:    string={value!r}\n"
            f"Expected: {expected}\n"
            f"Got:      {got}"
        )


def run_tests(path):
    fn = load_function(path)

    cases = [
        # Subject-style cases where there is no ambiguity.
        ("simple rising chain", "1234", 3),
        ("descending digits", "9876", 0),
        ("difference two only", "135", 0),
        ("no numeric chars", "abc", 0),

        # Empty/minimal cases.
        ("empty string", "", 0),
        ("one digit only", "1", 0),
        ("one letter only", "x", 0),
        ("digit then letter", "1a", 0),
        ("letter then digit", "a1", 0),

        # Adjacent numeric pair behavior.
        ("single valid pair", "12", 1),
        ("single invalid equal pair", "11", 0),
        ("single invalid descending pair", "21", 0),
        ("zero to one valid", "01", 1),
        ("eight to nine valid", "89", 1),
        ("nine to zero is not wrap", "90", 0),
        ("zero one after nine", "901", 1),

        # Multiple overlapping pairs.
        ("long full chain", "0123456789", 9),
        ("repeated chain", "123123", 4),
        ("overlap counted", "2345", 3),
        ("mixed rises and falls", "121212", 3),
        ("equal blocks", "111222333", 2),
        ("alternating valid invalid", "120120120", 5),

        # Non-numeric characters break adjacency under the provided correct behavior.
        ("letters break adjacency", "a1b2c3", 0),
        ("one adjacent pair inside letters", "a12b3", 1),
        ("punctuation breaks adjacency", "1-2", 0),
        ("spaces break adjacency", "1 2", 0),
        ("newline breaks adjacency", "1\n2", 0),
        ("tab breaks adjacency", "1\t2", 0),
        ("valid pairs around punctuation", "12-34", 2),
        ("valid pairs around letters", "ab12cd34ef", 2),
        ("digits separated by many chars", "1abc2def3", 0),

        # Punctuation/symbol stress.
        ("symbols only", "!@#$%", 0),
        ("symbols with one valid pair", "!!78??", 1),
        ("symbols with two valid pairs", "@01#89$", 2),

        # Unicode digits accepted because Python int(char) accepts them.
        ("arabic-indic digits valid", "١٢٣", 2),
        ("fullwidth digits valid", "１２３", 2),

        # Longer deterministic cases.
        ("many zeros", "0" * 100, 0),
        ("many increasing blocks", "0123456789" * 5, 45),
        ("many invalid descending blocks", "9876543210" * 5, 0),
    ]

    passed = 0

    for name, value, expected in cases:
        assert_case(fn, value, expected, name)
        passed += 1

    rng = random.Random(42)

    # Deterministic random mixed strings against reference behavior.
    alphabet = string.ascii_letters + string.digits + " !?_-.\n\t"
    for i in range(180):
        length = rng.randint(0, 160)
        value = "".join(rng.choice(alphabet) for _ in range(length))
        expected = reference(value)
        assert_case(fn, value, expected, f"random mixed string #{i + 1}")
        passed += 1

    # Deterministic digit-only random strings: catches off-by-one and wrong direction.
    for i in range(180):
        length = rng.randint(0, 160)
        value = "".join(rng.choice(string.digits) for _ in range(length))
        expected = reference(value)
        assert_case(fn, value, expected, f"random digit-only string #{i + 1}")
        passed += 1

    # Pattern-heavy tests: catch hardcoded samples and skip-across-non-digit mistakes.
    patterns = [
        "1234567890",
        "0123456789",
        "1212121212",
        "9090909090",
        "1a2b3c4d5",
        "12a23b34c45",
        "00112233445566778899",
    ]

    for i, pattern in enumerate(patterns, start=1):
        for repeat in (1, 2, 5, 10):
            value = pattern * repeat
            expected = reference(value)
            assert_case(fn, value, expected, f"pattern case #{i}, repeat {repeat}")
            passed += 1

    print(f"OK: {passed} tests passed")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_pattern_tracker_42.py pattern_tracker.py", file=sys.stderr)
        sys.exit(2)

    try:
        run_tests(sys.argv[1])
    except AssertionError as exc:
        print(f"KO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
