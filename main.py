
from wuas.loader import load_from_file
from wuas.validator import validate
from wuas.config import ConfigFile
from wuas.output.image import render_image
from wuas.output.json import render_to_json
from wuas.output.data import render_to_data_file
from wuas.args import parse_and_interpret_args

import sys
import json

args = parse_and_interpret_args()
config = ConfigFile.from_json(args.config_filename)
board = load_from_file(args.input_filename)
if args.validate:
    validate(config, board)

args.output_producer.produce_output(config, board)
