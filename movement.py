
from wuas.movement.prolog import parse_prolog


# TESTING
with open('/home/silvio/Documents/example_wuas.pl') as f:
    res = parse_prolog(f.read())
    print(res)
