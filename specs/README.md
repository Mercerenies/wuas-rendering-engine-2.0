
JSON Schema files for the file formats are available here. There are
three file formats used in processing WUAS data.

* The JSON configuration format specifies the configuration for a
  single game of WUAS, including a link to the JSON definitions file
  and to the image data for the game. The configuration file is read
  by this tool but never exported publicly.
* The JSON definition format (Schema in progress) contains definitions
  for tokens and spaces for a single game of WUAS and also contains
  interactive game board data. The definition file is read by this
  tool and also used by the public JavaScript renderer.
* The [JSON codex format](codex-schema.json) is not used directly by
  this tool but is used in the JavaScript renderer. The codex is a
  single JSON file that serves as ground truth for /all/ games of WUAS
  run by one host. It links to several definitions file for various
  WUAS games.
