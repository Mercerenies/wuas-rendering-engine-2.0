
"""Parsing module which converts a Prolog-lite DSL into a WuasTurn.
See WuasTurnParser."""

from attrs import define

from typing import Iterable

from wuas.board import Board
from wuas.config import ConfigFile
from wuas.movement.prolog import HornClause, Call
from wuas.movement.turn import WuasTurn, TurnSegment, TurnKey, PlayerTurnKey, Global
from wuas.movement.events import Event
from .assertions import assert_atom
from .error import ParseError


__all__ = (
    'WuasTurnParser', 'ParseError',
)


@define(eq=False, kw_only=True)
class WuasTurnParser:
    """Parser for WuasTurn objects."""
    _board: Board
    _config: ConfigFile

    def parse_prolog(self, data: Iterable[HornClause]) -> WuasTurn:
        """Parses Horn clauses as a WuasTurn object. Raises ParseError on failure."""
        return WuasTurn(self._parse_clause(clause) for clause in data)

    def _parse_clause(self, horn_clause: HornClause) -> TurnSegment:
        turn_key = self._parse_clause_head(horn_clause.head)
        exprs = [self._parse_expr(call) for call in horn_clause.body]
        return TurnSegment(turn_key, exprs)

    def _parse_clause_head(self, horn_clause_head: Call) -> TurnKey:
        head_atom = assert_atom(horn_clause_head)
        if head_atom == Global.KEY_NAME:
            return Global()
        else:
            _assert_is_player(self._config, head_atom)
            return PlayerTurnKey(player_id=head_atom)

    def _parse_expr(self, call: Call) -> Event:
        raise RuntimeError("Not implemented")  # TODO


def _assert_is_player(config: ConfigFile, token_id: str) -> None:
    try:
        player_token = config.definitions.get_token(token_id)
    except KeyError:
        raise ParseError(f"Unknown player ID {token_id!r}")
    if not player_token.is_player():
        raise ParseError(f"Expected player ID, got non-player token {player_token!r}")
