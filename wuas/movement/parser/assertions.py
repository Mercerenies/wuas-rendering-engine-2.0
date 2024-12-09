
from __future__ import annotations

from wuas.movement.prolog import Call, Atom
from wuas.movement.direction import Direction
from .error import ParseError


def assert_atom(call: Call) -> Atom:
    if call.args:
        raise ParseError(f"Expected an atom, got call {call!r}")
    return call.head


def assert_head(call: Call, expected_head: str) -> None:
    if call.head != expected_head:
        raise ParseError(f"Expected call {expected_head!r}, got call {call!r}")


def assert_arity(call: Call, arity: int) -> None:
    if len(call.args) != arity:
        raise ParseError(f"Expected call with {arity} argument(s), got call {call!r}")


def assert_list(call: Call) -> tuple[Call, ...]:
    assert_head(call, expected_head=Call.LIST_FUNCTION)
    return call.args


def assert_direction(call_or_atom: Atom | Call, /) -> Direction:
    atom = assert_atom(call_or_atom) if isinstance(call_or_atom, Call) else call_or_atom
    try:
        return Direction(atom)
    except ValueError:
        raise ParseError(f"Expected a direction, got atom {atom!r}")
