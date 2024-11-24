
"""The WUAS rendering engine 2.0. See README.md for more, or use --help
for help with the command line arguments."""

from wuas.loader import load_from_file
from wuas.validator import validate
from wuas.config import ConfigFile
from wuas.args import parse_and_interpret_args

args = parse_and_interpret_args()
config = ConfigFile.from_json(args.config_filename)
board = load_from_file(args.input_filename)
if args.validate:
    validate(config, board)

for processor in args.board_processors:
    processor.run(config, board)

args.output_producer.produce_output(config, board, args.to_output_args())
