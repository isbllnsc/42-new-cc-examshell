#!/usr/bin/env python3
"""
42-style hidden tester for permutation_checker.

Usage:
    python3 test_permutation_checker_42.py permutation_checker.py

Subject:
    Write a function:
        def permutation_checker(s: str, t: str) -> bool

Function-only rule:
    Because the subject asks for a FUNCTION, the submitted file must not execute
    anything at top level.

Allowed:
    - imports
    - constants
    - helper functions
    - the required permutation_checker function

Rejected:
    - main()
    - print(...) at top level
    - input(...) at top level
    - calls at top level
    - if __name__ == "__main__"
    - any import-time output

Behavior tested:
    Return True if both strings contain exactly the same characters with exactly
    the same counts.

Important:
    The subject example says "Listen" and "Silent" should be True, but the
    provided correct implementation uses sorted(s) == sorted(t), so behavior is
    case-sensitive.

    Therefore:
        permutation_checker("Listen", "Silent") -> False

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


REQUIRED_FUNCTION = "permutation_checker"


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


def reference(s, t):
    return sorted(s) == sorted(t)


def assert_case(fn, s, t, expected, name):
    try:
        got = fn(s, t)
    except Exception as exc:
        fail(
            f"{name}: function raised {type(exc).__name__}: {exc}\n"
            f"Input: s={s!r}, t={t!r}"
        )

    if type(got) is not bool:
        fail(
            f"{name}: function must return a bool, got {type(got).__name__}\n"
            f"Input: s={s!r}, t={t!r}\n"
            f"Returned: {got!r}"
        )

    if got != expected:
        fail(
            f"{name}: wrong result\n"
            f"Input:    s={s!r}, t={t!r}\n"
            f"Expected: {expected}\n"
            f"Got:      {got}"
        )


def run_tests(path):
    fn = load_function(path)

    cases = [
        # Subject-style examples / equivalent behavior.
        ("basic true", "anagram", "nagaram", True),
        ("basic false", "rat", "car", False),
        ("same string", "abc", "abc", True),
        ("same letters different order", "amor", "roma", True),

        # Important inconsistency: case-sensitive reference behavior.
        ("case-sensitive Listen/Silent", "Listen", "Silent", False),
        ("case-sensitive true", "Listen", "netsLi", True),
        ("upper/lower counts differ", "Aa", "aa", False),
        ("same chars mixed case", "AaBb", "bBaA", True),

        # Length and character counts must match.
        ("missing one char", "abc", "ab", False),
        ("extra one char", "abc", "abcc", False),
        ("same set different counts", "aab", "abb", False),
        ("duplicate count true", "aabbcc", "abcabc", True),
        ("many duplicates false", "aaaab", "aaabb", False),

        # Empty and tiny inputs.
        ("both empty", "", "", True),
        ("left empty only", "", "a", False),
        ("right empty only", "a", "", False),
        ("single same", "x", "x", True),
        ("single different", "x", "y", False),

        # Spaces and punctuation count as real characters.
        ("spaces count true", "a b", "b a", True),
        ("spaces count false", "ab", "a b", False),
        ("many spaces true", "a  b", " b a", True),
        ("punctuation count true", "a!b?", "?ba!", True),
        ("punctuation count false", "abc!", "abc", False),

        # Digits and mixed characters.
        ("digits true", "123abc", "cba321", True),
        ("digits false", "1123", "1233", False),
        ("mixed symbols true", "a1!A", "!Aa1", True),
        ("mixed symbols false", "a1!A", "!aa1", False),

        # Unicode/accents are exact characters.
        ("accent exact true", "ação", "çãoa", True),
        ("accent mismatch", "acao", "ação", False),
        ("unicode exact true", "éèê", "êéè", True),

        # Whitespace characters are exact characters.
        ("newline true", "a\nb", "b\na", True),
        ("tab true", "a\tb", "\tba", True),
        ("newline vs space false", "a\nb", "a b", False),
    ]

    passed = 0

    for name, s, t, expected in cases:
        assert_case(fn, s, t, expected, name)
        passed += 1

    rng = random.Random(42)
    alphabet = string.ascii_letters + string.digits + " !?_-.\n\t"

    # Deterministic randomized valid permutations.
    for i in range(140):
        length = rng.randint(0, 80)
        s = "".join(rng.choice(alphabet) for _ in range(length))
        chars = list(s)
        rng.shuffle(chars)
        t = "".join(chars)

        assert_case(fn, s, t, True, f"random valid permutation #{i + 1}")
        passed += 1

    # Deterministic arbitrary strings against reference.
    for i in range(180):
        s = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 80)))
        t = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 80)))

        expected = reference(s, t)
        assert_case(fn, s, t, expected, f"random arbitrary pair #{i + 1}")
        passed += 1

    # Pattern-heavy cases: catch set-based and case-insensitive shortcuts.
    patterns = [
        ("aab", "aba"),
        ("aab", "abb"),
        ("Aa", "aA"),
        ("Aa", "aa"),
        ("112233", "332211"),
        ("112233", "1231233"),
        ("abc!!!", "!!!cba"),
    ]

    for i, (s, t) in enumerate(patterns, start=1):
        for repeat in (1, 2, 5, 10):
            ss = s * repeat
            tt = t * repeat
            expected = reference(ss, tt)
            assert_case(fn, ss, tt, expected, f"pattern case #{i}, repeat {repeat}")
            passed += 1

    print(f"OK: {passed} tests passed")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_permutation_checker_42.py permutation_checker.py", file=sys.stderr)
        sys.exit(2)

    try:
        run_tests(sys.argv[1])
    except AssertionError as exc:
        print(f"KO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
