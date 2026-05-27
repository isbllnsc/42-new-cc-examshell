#!/usr/bin/env python3
"""
42-style hidden tester for bracket_validator.

Usage:
    python3 test_bracket_validator_42.py bracket_validator.py

Subject:
    Write a function:
        def bracket_validator(s: str) -> bool

Function-only rule:
    Because the subject asks for a FUNCTION, the submitted file must not execute
    anything at top level.

Allowed:
    - imports
    - constants
    - helper functions
    - the required bracket_validator function

Rejected:
    - main()
    - print(...) at top level
    - input(...) at top level
    - calls at top level
    - if __name__ == "__main__"
    - any import-time output

Behavior tested:
    Return True if brackets are valid:
        - same type closes same type
        - correct order
        - every close has a matching open

The subject says the input string contains only:
    ( ) { } [ ]

So the mandatory behavioral tests focus on those characters only.
"""

import ast
import importlib.util
import io
import os
import random
import sys
from contextlib import redirect_stdout


REQUIRED_FUNCTION = "bracket_validator"


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
    stack = []
    pairs = {
        ")": "(",
        "]": "[",
        "}": "{",
    }

    for char in s:
        if char in "([{":
            stack.append(char)
        else:
            if not stack:
                return False
            if stack[-1] != pairs[char]:
                return False
            stack.pop()

    return stack == []


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
            f"Expected: {expected}\n"
            f"Got:      {got}"
        )


def make_valid_string(rng, depth):
    if depth <= 0:
        return ""

    opens = "([{"
    closes = {
        "(": ")",
        "[": "]",
        "{": "}",
    }

    result = ""
    groups = rng.randint(0, 4)

    for _ in range(groups):
        open_char = rng.choice(opens)
        inner = make_valid_string(rng, depth - 1)
        result += open_char + inner + closes[open_char]

    return result


def run_tests(path):
    fn = load_function(path)

    cases = [
        # Subject examples
        ("subject example: simple pair", "()", True),
        ("subject example: sequential pairs", "()[]{}", True),
        ("subject example: wrong type", "(]", False),

        # Empty/minimal inputs
        ("empty string", "", True),
        ("single open parenthesis", "(", False),
        ("single close parenthesis", ")", False),
        ("single open square", "[", False),
        ("single close square", "]", False),
        ("single open curly", "{", False),
        ("single close curly", "}", False),

        # Basic valid cases
        ("simple square", "[]", True),
        ("simple curly", "{}", True),
        ("many sequential parentheses", "()()()", True),
        ("many sequential mixed", "{}[]()[]{}", True),
        ("nested parentheses", "((()))", True),
        ("nested square", "[[[]]]", True),
        ("nested curly", "{{{}}}", True),
        ("nested mixed simple", "([])", True),
        ("nested mixed deep", "{[()]}", True),
        ("nested mixed deeper", "({[]})", True),
        ("sequential nested groups", "{[()]}([]){}", True),

        # Invalid ordering/type
        ("classic crossing", "([)]", False),
        ("wrong closing order", "({)}", False),
        ("curly crossing", "{[(])}", False),
        ("reversed pair", ")(", False),
        ("all closing then opening", ")]}[{(", False),
        ("same counts wrong order", "({[}])", False),
        ("same counts reversed", "}{", False),

        # Missing/extra brackets
        ("missing close at end", "(()", False),
        ("extra close at end", "())", False),
        ("missing close mixed", "{[()]", False),
        ("extra close mixed", "{[()]}]", False),
        ("missing open mixed", "[()]}", False),
        ("valid prefix invalid suffix", "()[]{}(", False),
        ("invalid prefix valid suffix", ")()[]{}", False),
        ("balanced count but invalid", "())(()", False),

        # Longer deterministic cases
        ("long valid repeated", "({[]})" * 100, True),
        ("long valid nested", "(" * 100 + ")" * 100, True),
        ("long invalid one extra open", "({[]})" * 100 + "(", False),
        ("long invalid one extra close", "({[]})" * 100 + ")", False),
        ("long crossing repeated", "([)]" * 80, False),
    ]

    passed = 0

    for name, s, expected in cases:
        assert_case(fn, s, expected, name)
        passed += 1

    # Deterministic random valid cases.
    # These catch hardcoded solutions and fragile nesting logic.
    rng = random.Random(42)

    for i in range(120):
        s = make_valid_string(rng, rng.randint(0, 8))
        assert_case(fn, s, True, f"random valid case #{i + 1}")
        passed += 1

    # Deterministic random arbitrary bracket-only cases.
    # Expected values come from a stack-based reference implementation.
    alphabet = "()[]{}"

    for i in range(200):
        length = rng.randint(0, 200)
        s = "".join(rng.choice(alphabet) for _ in range(length))
        expected = reference(s)
        assert_case(fn, s, expected, f"random arbitrary case #{i + 1}")
        passed += 1

    print(f"OK: {passed} tests passed")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_bracket_validator_42.py bracket_validator.py", file=sys.stderr)
        sys.exit(2)

    try:
        run_tests(sys.argv[1])
    except AssertionError as exc:
        print(f"KO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
