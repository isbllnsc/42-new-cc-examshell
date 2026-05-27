#!/usr/bin/env python3
"""
42-style hidden tester for whisper_cipher.

Usage:
    python3 test_whisper_cipher_42.py whisper_cipher.py

Subject:
    Write a function:
        def whisper_cipher(s: str, shift: int) -> str

Function-only rule:
    Because the subject asks for a FUNCTION, the submitted file must not execute
    anything at top level.

Allowed:
    - imports
    - constants
    - helper functions
    - the required whisper_cipher function

Rejected:
    - main()
    - print(...) at top level
    - input(...) at top level
    - calls at top level
    - if __name__ == "__main__"
    - any import-time output

Behavior tested:
    Return a NEW string where each alphabetical character is shifted by shift
    positions in the alphabet.
    - lowercase wraps within a-z
    - uppercase wraps within A-Z
    - case is preserved
    - non-alphabetical characters are unchanged
    - shift may be zero, positive, negative, or larger than 26

Important:
    The implementation does not need to be identical to the reference.
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


REQUIRED_FUNCTION = "whisper_cipher"


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


def reference(s, shift):
    result = ""

    for char in s:
        if "a" <= char <= "z":
            result += chr((ord(char) - ord("a") + shift) % 26 + ord("a"))
        elif "A" <= char <= "Z":
            result += chr((ord(char) - ord("A") + shift) % 26 + ord("A"))
        else:
            result += char

    return result


def assert_case(fn, s, shift, expected, name):
    try:
        got = fn(s, shift)
    except Exception as exc:
        fail(
            f"{name}: function raised {type(exc).__name__}: {exc}\n"
            f"Input: s={s!r}, shift={shift!r}"
        )

    if type(got) is not str:
        fail(
            f"{name}: function must return a str, got {type(got).__name__}\n"
            f"Input: s={s!r}, shift={shift!r}\n"
            f"Returned: {got!r}"
        )

    if got != expected:
        fail(
            f"{name}: wrong result\n"
            f"Input:    s={s!r}, shift={shift!r}\n"
            f"Expected: {expected!r}\n"
            f"Got:      {got!r}"
        )


def run_tests(path):
    fn = load_function(path)

    cases = [
        # Subject examples
        ("subject example: Hello +3", "Hello", 3, "Khoor"),
        ("subject example: abc +1", "abc", 1, "bcd"),
        ("subject example: Zebra +2", "Zebra!", 2, "Bgdtc!"),

        # Empty/minimal cases
        ("empty string", "", 3, ""),
        ("single lowercase no wrap", "a", 1, "b"),
        ("single uppercase no wrap", "A", 1, "B"),
        ("single lowercase wrap", "z", 1, "a"),
        ("single uppercase wrap", "Z", 1, "A"),
        ("single non-alpha", "!", 5, "!"),

        # Zero shift
        ("zero shift lowercase", "abcxyz", 0, "abcxyz"),
        ("zero shift uppercase", "ABCXYZ", 0, "ABCXYZ"),
        ("zero shift mixed", "Hello, World! 123", 0, "Hello, World! 123"),

        # Wraparound
        ("lowercase wrap many", "xyz", 3, "abc"),
        ("uppercase wrap many", "XYZ", 3, "ABC"),
        ("mixed wrap", "AbcXyz", 2, "CdeZab"),
        ("full alphabet +1", "abcdefghijklmnopqrstuvwxyz", 1, "bcdefghijklmnopqrstuvwxyza"),
        ("full alphabet upper +1", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 1, "BCDEFGHIJKLMNOPQRSTUVWXYZA"),

        # Negative shifts
        ("negative shift simple", "abc", -1, "zab"),
        ("negative shift uppercase", "ABC", -1, "ZAB"),
        ("negative shift mixed", "AbC zZ", -2, "YzA xX"),
        ("negative wrap full", "abcXYZ", -27, "zabWXY"),

        # Large shifts
        ("shift exactly alphabet size", "abcXYZ", 26, "abcXYZ"),
        ("shift double alphabet size", "abcXYZ", 52, "abcXYZ"),
        ("large positive shift", "abcXYZ", 53, "bcdYZA"),
        ("large negative shift", "abcXYZ", -53, "zabWXY"),
        ("huge positive shift", "Hello Zebra!", 1000003, reference("Hello Zebra!", 1000003)),
        ("huge negative shift", "Hello Zebra!", -1000003, reference("Hello Zebra!", -1000003)),

        # Non-alphabetical characters unchanged
        ("digits unchanged", "a1b2c3", 4, "e1f2g3"),
        ("punctuation unchanged", "a-b_c! 123", 4, "e-f_g! 123"),
        ("spaces tabs newlines unchanged", "A B\tC\nZ", 1, "B C\tD\nA"),
        ("symbols only", "1234!? _-+=", 99, "1234!? _-+="),

        # Case preservation
        ("mixed case pattern", "AbCdEfZz", 2, "CdEfGhBb"),
        ("case not normalized", "aA zZ", 1, "bB aA"),

        # Non-ASCII alphabetic characters follow provided implementation behavior.
        # The reference implementation uses isalpha() but ord('a')/'A' math,
        # which produces deterministic nonstandard output for accents.
        # To avoid punishing reasonable ASCII-only Caesar solutions, mandatory tests
        # focus on ASCII letters and non-letters only.
    ]

    passed = 0

    for name, s, shift, expected in cases:
        assert_case(fn, s, shift, expected, name)
        passed += 1

    rng = random.Random(42)
    alphabet = string.ascii_letters + string.digits + " !?_-.,:;[]{}()@#$%^&*+=/\\\n\t"

    # Deterministic random tests against reference behavior.
    for i in range(260):
        length = rng.randint(0, 180)
        s = "".join(rng.choice(alphabet) for _ in range(length))
        shift = rng.randint(-5000, 5000)

        expected = reference(s, shift)
        assert_case(fn, s, shift, expected, f"random mixed case #{i + 1}")
        passed += 1

    # Pattern-heavy tests: catch hardcoded samples, missing modulo, and wrong case handling.
    patterns = [
        "abcXYZ",
        "xyzXYZ",
        "Hello, World!",
        "Zebra!",
        "The Quick Brown Fox Jumps Over 13 Lazy Dogs.",
        "aA-zZ_0!",
    ]

    for i, pattern in enumerate(patterns, start=1):
        for shift in (-100, -53, -27, -26, -25, -1, 0, 1, 2, 25, 26, 27, 52, 53, 100):
            expected = reference(pattern, shift)
            assert_case(fn, pattern, shift, expected, f"pattern case #{i}, shift {shift}")
            passed += 1

    print(f"OK: {passed} tests passed")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_whisper_cipher_42.py whisper_cipher.py", file=sys.stderr)
        sys.exit(2)

    try:
        run_tests(sys.argv[1])
    except AssertionError as exc:
        print(f"KO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
