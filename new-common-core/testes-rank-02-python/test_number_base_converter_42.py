#!/usr/bin/env python3
"""
42-style hidden tester for number_base_converter.

Usage:
    python3 test_number_base_converter_42.py number_base_converter.py

Subject:
    Write a function:
        def number_base_converter(s: str, base_from: int, base_to: int) -> str

Function-only rule:
    Because the subject asks for a FUNCTION, the submitted file must not execute
    anything at top level.

Allowed:
    - imports
    - constants
    - helper functions
    - the required number_base_converter function

Rejected:
    - main()
    - print(...) at top level
    - input(...) at top level
    - calls at top level
    - if __name__ == "__main__"
    - any import-time output

Behavior tested:
    Convert a number represented as a string from base_from to base_to.
    Valid bases are 2 through 36.
    Digits are 0-9 and A-Z, with lowercase accepted as equivalent input.
    Invalid input/base returns "ERROR".

Important:
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


REQUIRED_FUNCTION = "number_base_converter"
DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


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


def to_base(value, base):
    if value == 0:
        return "0"

    result = ""
    while value > 0:
        result = DIGITS[value % base] + result
        value //= base
    return result


def reference(s, base_from, base_to):
    if not (2 <= base_from <= 36) or not (2 <= base_to <= 36):
        return "ERROR"

    if type(s) is not str:
        return "ERROR"

    s = s.strip().upper()

    if not s:
        return "ERROR"

    allowed = DIGITS[:base_from]
    value = 0

    for char in s:
        if char not in allowed:
            return "ERROR"
        value = value * base_from + DIGITS.index(char)

    return to_base(value, base_to)


def assert_case(fn, s, base_from, base_to, expected, name):
    try:
        got = fn(s, base_from, base_to)
    except Exception as exc:
        fail(
            f"{name}: function raised {type(exc).__name__}: {exc}\n"
            f"Input: s={s!r}, base_from={base_from!r}, base_to={base_to!r}"
        )

    if type(got) is not str:
        fail(
            f"{name}: function must return a str, got {type(got).__name__}\n"
            f"Input: s={s!r}, base_from={base_from!r}, base_to={base_to!r}\n"
            f"Returned: {got!r}"
        )

    if got != expected:
        fail(
            f"{name}: wrong result\n"
            f"Input:    s={s!r}, base_from={base_from!r}, base_to={base_to!r}\n"
            f"Expected: {expected!r}\n"
            f"Got:      {got!r}"
        )


def run_tests(path):
    fn = load_function(path)

    cases = [
        # Subject examples
        ("subject example: binary to decimal", "1011", 2, 10, "11"),
        ("subject example: hex to binary", "1A", 16, 2, "11010"),
        ("subject example: hex FF to decimal", "FF", 16, 10, "255"),

        # Minimal values and zero
        ("zero base10 to binary", "0", 10, 2, "0"),
        ("zero binary to base36", "0", 2, 36, "0"),
        ("single digit same base", "7", 10, 10, "7"),
        ("single max base36 digit", "Z", 36, 10, "35"),
        ("lowercase accepted", "z", 36, 10, "35"),
        ("mixed lowercase accepted", "ff", 16, 10, "255"),
        ("mixed case accepted", "aB", 16, 10, "171"),

        # Base conversions
        ("decimal to binary", "255", 10, 2, "11111111"),
        ("decimal to hex", "255", 10, 16, "FF"),
        ("decimal to base36", "255", 10, 36, "73"),
        ("base36 to decimal", "ZZ", 36, 10, "1295"),
        ("base36 to binary", "10", 36, 2, "100100"),
        ("base2 to base36", "1111111111", 2, 36, "SF"),
        ("base8 to base16", "755", 8, 16, "1ED"),
        ("base16 to base8", "1ED", 16, 8, "755"),

        # Leading zeros should not affect numeric value
        ("leading zeros decimal", "000123", 10, 10, "123"),
        ("leading zeros binary", "0001011", 2, 10, "11"),
        ("all zeros", "0000", 10, 16, "0"),

        # Leading/trailing whitespace tolerated defensively
        ("leading whitespace", "   FF", 16, 10, "255"),
        ("trailing whitespace", "FF   ", 16, 10, "255"),
        ("leading and trailing whitespace", "\t1011\n", 2, 10, "11"),

        # Invalid bases
        ("base_from too low", "10", 1, 10, "ERROR"),
        ("base_from zero", "10", 0, 10, "ERROR"),
        ("base_from negative", "10", -2, 10, "ERROR"),
        ("base_from too high", "10", 37, 10, "ERROR"),
        ("base_to too low", "10", 10, 1, "ERROR"),
        ("base_to zero", "10", 10, 0, "ERROR"),
        ("base_to negative", "10", 10, -8, "ERROR"),
        ("base_to too high", "10", 10, 37, "ERROR"),

        # Invalid digits for base
        ("digit 2 invalid in binary", "102", 2, 10, "ERROR"),
        ("digit 8 invalid in octal", "128", 8, 10, "ERROR"),
        ("G invalid in hex", "1G", 16, 10, "ERROR"),
        ("Z invalid in base35", "Z", 35, 10, "ERROR"),
        ("letter invalid in decimal", "12A", 10, 2, "ERROR"),

        # Invalid characters
        ("empty string", "", 10, 2, "ERROR"),
        ("spaces only", "   ", 10, 2, "ERROR"),
        ("punctuation invalid", "1A!", 16, 10, "ERROR"),
        ("internal space invalid", "1 A", 16, 10, "ERROR"),
        ("underscore invalid", "1_A", 16, 10, "ERROR"),
        ("sign not supported", "-10", 10, 2, "ERROR"),
        ("plus sign not supported", "+10", 10, 2, "ERROR"),

        # Larger numbers
        ("large decimal to hex", "123456789", 10, 16, "75BCD15"),
        ("large hex to decimal", "ABCDEF", 16, 10, "11259375"),
        ("large base36 to decimal", "HELLO", 36, 10, "29234652"),
        ("large decimal to base36", "987654321", 10, 36, "GC0UY9"),
    ]

    passed = 0

    for name, s, base_from, base_to, expected in cases:
        assert_case(fn, s, base_from, base_to, expected, name)
        passed += 1

    rng = random.Random(42)

    # Deterministic random valid conversions.
    for i in range(250):
        base_from = rng.randint(2, 36)
        base_to = rng.randint(2, 36)
        value = rng.randint(0, 10**12)

        s = to_base(value, base_from)

        # Randomly lowercase some letters to ensure case-insensitive input.
        chars = []
        for char in s:
            if char.isalpha() and rng.random() < 0.5:
                chars.append(char.lower())
            else:
                chars.append(char)
        s = "".join(chars)

        expected = reference(s, base_from, base_to)
        assert_case(fn, s, base_from, base_to, expected, f"random valid conversion #{i + 1}")
        passed += 1

    # Deterministic random invalid strings/bases.
    invalid_chars = "!@#$%^&*()_-+=[]{};:'\",.<>?/\\| "
    for i in range(120):
        base_from = rng.randint(2, 36)
        base_to = rng.randint(2, 36)

        length = rng.randint(1, 20)
        s = "".join(rng.choice(DIGITS + invalid_chars) for _ in range(length))

        # Force at least one invalid char for the base.
        s += rng.choice(invalid_chars)

        expected = "ERROR"
        assert_case(fn, s, base_from, base_to, expected, f"random invalid string #{i + 1}")
        passed += 1

    # Pattern-heavy tests: catch hardcoding and off-by-one digit/base logic.
    patterns = [
        ("10", 2),
        ("101010", 2),
        ("777", 8),
        ("999", 10),
        ("FFF", 16),
        ("ZZZ", 36),
        ("123456789", 10),
    ]

    for i, (s, base_from) in enumerate(patterns, start=1):
        for base_to in range(2, 37):
            expected = reference(s, base_from, base_to)
            assert_case(fn, s, base_from, base_to, expected, f"pattern case #{i}, base_to {base_to}")
            passed += 1

    print(f"OK: {passed} tests passed")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_number_base_converter_42.py number_base_converter.py", file=sys.stderr)
        sys.exit(2)

    try:
        run_tests(sys.argv[1])
    except AssertionError as exc:
        print(f"KO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
