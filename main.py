
from wuas.loader import load_from_file
from wuas.validator import validate
from wuas.config import ConfigFile
from wuas.output.image import render_image

# Testing
board = load_from_file('/home/silvio/Documents/wuas_2023/turn2.dat')
config = ConfigFile.from_json('/home/silvio/Documents/wuas_2023/config.json')
print(board)
validate(config, board)
image = render_image(config, board)
image.show()
