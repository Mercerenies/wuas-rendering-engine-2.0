
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
    head: Call
    conditions: tuple[Call, ...]


@dataclass(frozen=True)
class Call:
    head: Atom
    args: tuple[Call, ...] = ()

    LIST_FUNCTION = Atom('[]')

    def __repr__(self) -> str:
        if self.args:
            args_str = ', '.join(map(repr, self.args))
            return f"Call({self.head!r}, [{args_str}])"
        else:
            return f"Call({self.head!r})"

    @classmethod
    def list(cls, args: tuple[Call, ...]) -> Call:
        return cls(cls.LIST_FUNCTION, args)


class PrologLarkTransformer(Transformer):

    def start(self, items: list[HornClause]) -> tuple[HornClause, ...]:
        return tuple(items)

    def horn_clause(self, items: list[Call]) -> HornClause:
        head, *conditions = items
        return HornClause(head, tuple(conditions))

    def atom(self, items: list[Token]) -> Call:
        return Call(Atom(str(items[0])), ())

    def function_call(self, items: list[Any]) -> Call:
        head, *args = items
        return Call(Atom(str(head)), tuple(args))

    def list(self, items: list[Call]) -> Call:
        return Call.list(tuple(items))


def parse_prolog(text: str) -> tuple[HornClause, ...]:
    tokens = _lark_parser.parse(text)
    return PrologLarkTransformer().transform(tokens)
