#!/usr/bin/env python3
"""
42-style hidden tester for crypto_sorter.

Usage:
    python3 test_crypto_sorter_42.py crypto_sorter.py

Subject:
    Write a function:
        def crypto_sorter(words: List[str]) -> List[str]

Function-only rule:
    Because the subject asks for a FUNCTION, the submitted file must not execute
    anything at top level.

Allowed:
    - imports
    - constants
    - helper functions
    - the required crypto_sorter function

Rejected:
    - main()
    - print(...) at top level
    - input(...) at top level
    - calls at top level
    - if __name__ == "__main__"
    - any import-time output

Behavior tested:
    Return a sorted NEW list using these keys:
        1. length ascending
        2. ASCII/Unicode code point lexicographical order
        3. number of vowels ascending

Reference-equivalent key:
    key=lambda w: (len(w), [ord(c) for c in w], count_vowels(w))

Important:
    The input list must not be mutated.
"""

import ast
import importlib.util
import io
import os
import random
import string
import sys
from contextlib import redirect_stdout


REQUIRED_FUNCTION = "crypto_sorter"


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


def count_vowels(s):
    return sum(1 for c in s.lower() if c in "aeiou")


def reference(words):
    return sorted(words, key=lambda w: (len(w), [ord(c) for c in w], count_vowels(w)))


def assert_case(fn, words, expected, name):
    original = list(words)

    try:
        got = fn(words)
    except Exception as exc:
        fail(
            f"{name}: function raised {type(exc).__name__}: {exc}\n"
            f"Input: words={original!r}"
        )

    if type(got) is not list:
        fail(
            f"{name}: function must return a list, got {type(got).__name__}\n"
            f"Input: words={original!r}\n"
            f"Returned: {got!r}"
        )

    if got != expected:
        fail(
            f"{name}: wrong result\n"
            f"Input:    words={original!r}\n"
            f"Expected: {expected!r}\n"
            f"Got:      {got!r}"
        )

    if words != original:
        fail(
            f"{name}: function mutated the input list\n"
            f"Before: {original!r}\n"
            f"After:  {words!r}"
        )

    if got is words:
        fail(
            f"{name}: function returned the original list object. "
            "Return a new sorted list instead."
        )


def run_tests(path):
    fn = load_function(path)

    cases = [
        # Subject examples
        (
            "subject example 1",
            ["apple", "Banana", "kiwi", "orange", "Egg"],
            ["Egg", "kiwi", "apple", "Banana", "orange"],
        ),
        (
            "subject example 2",
            ["a", "bb", "ccc", "dd"],
            ["a", "bb", "dd", "ccc"],
        ),
        (
            "subject example 3",
            ["abc", "acb", "bac"],
            ["abc", "acb", "bac"],
        ),

        # Empty/minimal inputs
        ("empty list", [], []),
        ("single empty string", [""], [""]),
        ("single word", ["zebra"], ["zebra"]),
        ("empty string sorts first", ["a", "", "bb"], ["", "a", "bb"]),

        # Length comes first
        (
            "length primary key",
            ["aaaa", "z", "bb", "ccc"],
            ["z", "bb", "ccc", "aaaa"],
        ),
        (
            "short uppercase before longer lowercase",
            ["zz", "A", "b", "ccc"],
            ["A", "b", "zz", "ccc"],
        ),

        # ASCII lexicographical order for same length
        (
            "ascii uppercase before lowercase",
            ["a", "Z", "A", "z"],
            ["A", "Z", "a", "z"],
        ),
        (
            "ascii punctuation and digits",
            ["b", "A", "1", "_", "!"],
            ["!", "1", "A", "_", "b"],
        ),
        (
            "same length lexicographic",
            ["ba", "ab", "aa", "BB", "Aa"],
            ["Aa", "BB", "aa", "ab", "ba"],
        ),
        (
            "ascii not case-insensitive",
            ["apple", "Apple", "APPLE", "apPle"],
            ["APPLE", "Apple", "apPle", "apple"],
        ),

        # Duplicates must be preserved
        (
            "duplicates preserved",
            ["bb", "a", "bb", "aa", "a"],
            ["a", "a", "aa", "bb", "bb"],
        ),
        (
            "all equal strings",
            ["same", "same", "same"],
            ["same", "same", "same"],
        ),

        # Vowels do not override ASCII order.
        # These catch solutions that sort by length then vowel count before lexicographic order.
        (
            "ascii before vowel count",
            ["bbb", "aaa", "ccc"],
            ["aaa", "bbb", "ccc"],
        ),
        (
            "vowel key is after ascii key",
            ["zz", "aa", "bb", "ee"],
            ["aa", "bb", "ee", "zz"],
        ),

        # Mixed lengths, symbols, and cases
        (
            "mixed tricky",
            ["", "B", "a", "AA", "A!", "!!", "aaa", "ZZ", "zz"],
            ["", "B", "a", "!!", "A!", "AA", "ZZ", "zz", "aaa"],
        ),
        (
            "numbers as strings",
            ["10", "2", "01", "9", "100", "00"],
            ["2", "9", "00", "01", "10", "100"],
        ),

        # Unicode/code point order should work because ord() is used.
        (
            "unicode code point order",
            ["é", "a", "Á", "z"],
            ["a", "z", "Á", "é"],
        ),
    ]

    passed = 0

    for name, words, expected in cases:
        assert_case(fn, list(words), expected, name)
        passed += 1

    rng = random.Random(42)

    alphabet = string.ascii_letters + string.digits + "!_-.?"
    for i in range(250):
        size = rng.randint(0, 60)
        words = []
        for _ in range(size):
            length = rng.randint(0, 12)
            word = "".join(rng.choice(alphabet) for _ in range(length))
            words.append(word)

        expected = reference(words)
        assert_case(fn, list(words), expected, f"random mixed case #{i + 1}")
        passed += 1

    # Pattern-heavy tests: catch hardcoded samples and wrong key order.
    patterns = [
        ["aaa", "bbb", "ccc", "ddd", "eee"],
        ["A", "a", "B", "b", "0", "_", "!"],
        ["abc", "acb", "bac", "bca", "cab", "cba"],
        ["", "x", "xx", "xxx", "xxxx"],
        ["Egg", "kiwi", "apple", "Banana", "orange"],
    ]

    for i, words in enumerate(patterns, start=1):
        for repeat in (1, 2, 5):
            candidate = words * repeat
            rng.shuffle(candidate)
            expected = reference(candidate)
            assert_case(fn, list(candidate), expected, f"pattern case #{i}, repeat {repeat}")
            passed += 1

    print(f"OK: {passed} tests passed")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_crypto_sorter_42.py crypto_sorter.py", file=sys.stderr)
        sys.exit(2)

    try:
        run_tests(sys.argv[1])
    except AssertionError as exc:
        print(f"KO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
