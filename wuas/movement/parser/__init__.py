
"""Parsing module which converts a Prolog-lite DSL into a WuasTurn.
See WuasTurnParser."""

from attrs import define

from typing import Iterable

from wuas.board import Board
from wuas.config import ConfigFile
from wuas.movement.prolog import parse_prolog, HornClause, Call
from wuas.movement.turn import WuasTurn, TurnSegment, TurnKey, PlayerTurnKey, Global
from wuas.movement.events import Event
from wuas.movement.direction import Direction
from .assertions import assert_atom
from .error import ParseError
from .functions import BUILT_IN_FUNCTIONS


__all__ = (
    'WuasTurnParser', 'ParseError',
    'BUILT_IN_FUNCTIONS',
)


@define(eq=False, kw_only=True)
class WuasTurnParser:
    """Parser for WuasTurn objects."""
    _board: Board
    _config: ConfigFile

    def parse_clauses(self, data: Iterable[HornClause]) -> WuasTurn:
        """Parses Horn clauses as a WuasTurn object. Raises ParseError on failure."""
        return WuasTurn(self._parse_clause(clause) for clause in data)

    def parse(self, text: str) -> WuasTurn:
        """Parses text as Prolog, then as a WuasTurn object. Raises
        ParseError on failure."""
        prolog_data = parse_prolog(text)
        return self.parse_clauses(prolog_data)

    def _parse_clause(self, horn_clause: HornClause) -> TurnSegment:
        turn_key = self._parse_clause_head(horn_clause.head)
        stmts = [self._parse_stmt(call) for call in horn_clause.body]
        return TurnSegment(turn_key, stmts)

    def _parse_clause_head(self, horn_clause_head: Call) -> TurnKey:
        head_atom = assert_atom(horn_clause_head)
        if head_atom == Global.KEY_NAME:
            return Global()
        else:
            _assert_is_player(self._config, head_atom)
            return PlayerTurnKey(player_id=head_atom)

    def _parse_stmt(self, call: Call) -> Event:
        call = self._transform_direction_stmt(call)
        try:
            function = BUILT_IN_FUNCTIONS[call.head]
        except KeyError:
            raise ParseError(f"Unknown function {call.head!r}")
        return function(call)

    def _transform_direction_stmt(self, call: Call) -> Call:
        """As a convenience, we treat barenames which are valid
        cardinal directions as calls to the "go" function. So `left`
        is treated as `go(left)`.

        """
        try:
            atom = assert_atom(call)
            if atom in Direction:
                return Call("go", (call,))
        except ParseError:
            pass
        return call


def _assert_is_player(config: ConfigFile, token_id: str) -> None:
    try:
        player_token = config.definitions.get_token(token_id)
    except KeyError:
        raise ParseError(f"Unknown player ID {token_id!r}")
    if not player_token.is_player():
        raise ParseError(f"Expected player ID, got non-player token {player_token!r}")
