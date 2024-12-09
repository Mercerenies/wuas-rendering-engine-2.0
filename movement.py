
from wuas.movement import WuasTurn, WuasTurnEvaluator, WuasTurnParser
from wuas.movement.args import parse_and_interpret_args
from wuas.validator import validate
from wuas.config import ConfigFile
from wuas.loader import load_from_file


if __name__ == "__main__":
    args = parse_and_interpret_args()
    config = ConfigFile.from_json(args.config_filename)
    board = load_from_file(args.input_filename)
    if args.validate:
        validate(config, board)

    evaluator = WuasTurnEvaluator(board=board, config=config)

    turn_parser = WuasTurnParser(board=board, config=config)
    with open(args.turn_log_file, 'r') as f:
        turn_data = turn_parser.parse(f.read())
        for player_id, _ in config.definitions.all_players():
            logs = evaluator.evaluate_turn(turn_data, player_id)
            print(player_id)
            for log_message in logs:
                print(" * ", log_message, sep='')
