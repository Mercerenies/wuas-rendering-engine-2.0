
from wuas.loader import load_from_file
from wuas.validator import validate
from wuas.config import ConfigFile
from wuas.output.image import render_image
from wuas.output.json import render_to_json

import json

# Testing
board = load_from_file('/home/silvio/Documents/wuas_2023/turn2_newformat.dat')
config = ConfigFile.from_json('/home/silvio/Documents/wuas_2023/config.json')
print(board)
validate(config, board)

image = render_image(config, board)
image.show()

json_data = render_to_json(board)
print(json.dumps(json_data))
