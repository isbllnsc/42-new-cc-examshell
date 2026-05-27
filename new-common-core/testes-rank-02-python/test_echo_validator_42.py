#!/usr/bin/env python3
"""
42-style hidden tester for echo_validator.

Usage:
    python3 test_echo_validator_42.py echo_validator.py

Subject:
    Write a function:
        def echo_validator(s: str) -> bool

Function-only rule:
    Because the subject asks for a FUNCTION, the submitted file must not execute
    anything at top level.

Allowed:
    - imports
    - constants
    - helper functions
    - the required echo_validator function

Rejected:
    - main()
    - print(...) at top level
    - input(...) at top level
    - calls at top level
    - if __name__ == "__main__"
    - any import-time output

Behavior tested:
    Return True if, after converting to lowercase and removing all
    non-alphanumeric characters, the string reads the same forward and backward.
"""

import ast
import importlib.util
import io
import os
import random
import string
import sys
from contextlib import redirect_stdout


REQUIRED_FUNCTION = "echo_validator"


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
    filtered = "".join(char.lower() for char in s if char.isalnum())
    return filtered == filtered[::-1]


def assert_case(fn, s, expected, name):
    try:
        got = fn(s)
    except Exception as exc:
        fail(
            f"{name}: function raised {type(exc).__name__}: {exc}\n"
            f"Input: s={s!r}"
        )

    if type(got) is not bool:
        fail(
            f"{name}: function must return a bool, got {type(got).__name__}\n"
            f"Input: s={s!r}\n"
            f"Returned: {got!r}"
        )

    if got != expected:
        fail(
            f"{name}: wrong result\n"
            f"Input:    s={s!r}\n"
            f"Processed: {''.join(char.lower() for char in s if char.isalnum())!r}\n"
            f"Expected: {expected}\n"
            f"Got:      {got}"
        )


def make_palindrome(rng, alphabet):
    half_len = rng.randint(0, 60)
    half = "".join(rng.choice(alphabet) for _ in range(half_len))
    middle = rng.choice(alphabet) if rng.random() < 0.5 else ""
    return half + middle + half[::-1]


def add_noise(rng, s):
    noise = " ,.:;!?-_()[]{}'\"/\\\n\t"
    result = ""
    for char in s:
        if rng.random() < 0.35:
            result += "".join(rng.choice(noise) for _ in range(rng.randint(1, 3)))
        result += char
        if rng.random() < 0.35:
            result += "".join(rng.choice(noise) for _ in range(rng.randint(1, 3)))
    return result


def run_tests(path):
    fn = load_function(path)

    cases = [
        # Subject examples
        ("subject example: Panama", "A man, a plan, a canal: Panama", True),
        ("subject example: race a car", "race a car", False),
        ("subject example: blank space", " ", True),

        # Empty/minimal cases
        ("empty string", "", True),
        ("single lowercase letter", "a", True),
        ("single uppercase letter", "Z", True),
        ("single digit", "7", True),
        ("single punctuation", "!", True),
        ("only punctuation", ".,;:!? -_", True),
        ("only whitespace", " \t\n\r", True),

        # Case-insensitivity
        ("mixed case simple true", "Aa", True),
        ("mixed case palindrome", "RaceCar", True),
        ("case-insensitive false", "RaceCarX", False),
        ("upper/lower with punctuation", "No 'x' in Nixon", True),

        # Non-alphanumeric characters ignored
        ("punctuation ignored true", "Madam, I'm Adam.", True),
        ("punctuation ignored false", "Madam, I'm Adams.", False),
        ("spaces ignored true", "n u r s e s r u n", True),
        ("symbols ignored true", "!!!r@a#c$e%c^a&r!!!", True),
        ("symbols ignored false", "!!!r@a#c$e%x^a&r!!!", False),

        # Digits count as alphanumeric
        ("digits palindrome", "12321", True),
        ("digits not palindrome", "123421", False),
        ("letters and digits true", "A1b2b1a", True),
        ("letters and digits false", "A1b2c1a", False),
        ("punctuated digits true", "1,2,3,2,1", True),
        ("punctuated digits false", "1,2,3,4,1", False),

        # Classic tricky phrases
        ("classic phrase 1", "Was it a car or a cat I saw?", True),
        ("classic phrase 2", "Eva, can I see bees in a cave?", True),
        ("classic phrase 3", "Mr. Owl ate my metal worm", True),
        ("classic phrase false", "This is not a palindrome", False),

        # Unicode/alnum behavior follows Python isalnum/lower behavior
        ("accent palindrome true", "Ábá", True),
        ("accent false", "ábca", False),
        ("unicode digits true", "١٢٣٢١", True),

        # Long deterministic cases
        ("long palindrome letters", "a" * 500 + "b" + "a" * 500, True),
        ("long non-palindrome letters", "a" * 500 + "bc" + "a" * 500, False),
        ("long punctuation only", "!" * 1000, True),
    ]

    passed = 0

    for name, s, expected in cases:
        assert_case(fn, s, expected, name)
        passed += 1

    rng = random.Random(42)
    alnum = string.ascii_letters + string.digits

    # Deterministic random palindromes with punctuation/noise.
    for i in range(160):
        base = make_palindrome(rng, alnum)
        noisy = add_noise(rng, base)
        assert_case(fn, noisy, True, f"random noisy palindrome #{i + 1}")
        passed += 1

    # Deterministic random arbitrary strings against reference implementation.
    alphabet = string.ascii_letters + string.digits + " ,.:;!?-_()[]{}'\"/\\\n\t"
    for i in range(220):
        length = rng.randint(0, 220)
        s = "".join(rng.choice(alphabet) for _ in range(length))
        expected = reference(s)
        assert_case(fn, s, expected, f"random arbitrary case #{i + 1}")
        passed += 1

    # Pattern-heavy cases to catch hardcoded or punctuation/case mistakes.
    patterns = [
        "ab",
        "abc",
        "abba",
        "abcba",
        "A_b-b_a",
        "1a2b2a1",
        "123454321",
        "123456789",
    ]

    for i, pattern in enumerate(patterns, start=1):
        for repeat in (1, 2, 5, 10):
            s = add_noise(rng, pattern * repeat)
            expected = reference(s)
            assert_case(fn, s, expected, f"pattern case #{i}, repeat {repeat}")
            passed += 1

    print(f"OK: {passed} tests passed")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_echo_validator_42.py echo_validator.py", file=sys.stderr)
        sys.exit(2)

    try:
        run_tests(sys.argv[1])
    except AssertionError as exc:
        print(f"KO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
