
"""Implementation of a subset of the Prolog programming language's
syntax, for use as a DSL.

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NewType, Any

from lark import Lark, Transformer, Token

from wuas.util import project_root

with open(project_root() / 'res' / 'prolog.lark', 'r') as f:
    _lark_parser = Lark(f)


Atom = NewType('Atom', str)


@dataclass(frozen=True)
class HornClause:
    """A horn clause consists of an expression as the head and a
    sequence of expressions as the body.

    """
    head: Call
    body: tuple[Call, ...]


@dataclass(frozen=True)
class Call:
    """An expression, or function call, in the Prolog-lite DSL."""

    head: Atom
    args: tuple[Call, ...] = ()

    LIST_FUNCTION = Atom('[]')

    def __repr__(self) -> str:
        """A user-friendly, yet still Python-readable representation
        of the call."""
        if self.args:
            args_str = ', '.join(map(repr, self.args))
            return f"Call({self.head!r}, [{args_str}])"
        else:
            return f"Call({self.head!r})"

    @classmethod
    def list(cls, args: tuple[Call, ...]) -> Call:
        """A call representing a list of values. Note that we deviate
        from standard Prolog here. Standard Prolog represents lists as
        forward-linked lists with head `[|]`, similar to Lisp.
        Instead, we find it more convenient in our use case to
        represent lists as flat, non-linked calls to `[]`.

        """
        return cls(cls.LIST_FUNCTION, args)


class PrologLarkTransformer(Transformer):
    """Lark transformer for the Prolog-lite DSL."""

    def start(self, items: list[HornClause]) -> tuple[HornClause, ...]:
        return tuple(items)

    def horn_clause(self, items: list[Call]) -> HornClause:
        head, *body = items
        return HornClause(head, tuple(body))

    def atom(self, items: list[Token]) -> Call:
        return Call(Atom(str(items[0])), ())

    def function_call(self, items: list[Any]) -> Call:
        head, *args = items
        return Call(Atom(str(head)), tuple(args))

    def list(self, items: list[Call]) -> Call:
        return Call.list(tuple(items))


def parse_prolog(text: str) -> tuple[HornClause, ...]:
    """Parses a Prolog-lite program as a sequence of horn clauses."""
    tokens = _lark_parser.parse(text)
    return PrologLarkTransformer().transform(tokens)
