
# The WUAS Datafile

## Specification

This page describes the Wish Upon A Star datafile format. This is a
text-based format designed to be easy to view and edit by hand in an
ordinary text editor.

Unless otherwise stated, this page describes the most recent version
of the file format. The most recent version of the file format is
Version 5. A history of the file format versions is available at the
bottom of this page.

Unless otherwise stated, every part of this file format is case
sensitive.

By convention, a WUAS datafile uses the file extension `.dat`, though
this is not a requirement. WUAS datafiles are always stored in UTF-8.

The structure of a WUAS file format is summarized by the following
EBNF grammar. Note that many sections are separated by mandatory blank
lines. Trailing newlines at the very end of the file MAY be omitted.

```
datafile = header "\n" { floor-data "\n\n" } "\n" footer ;
header = { leading-comment "\n" } "\n" version-number "\n" { metadata "\n" } ;
version-number = integer
metadata = name ": " (* any string *)
floor-data = "floor=" integer "\n" floor-contents ;
floor-contents = (* see below *) ;
footer = { token-data "\n" } "\n" { attribute-data "\n" } "\n" { graph-data "\n" } ;
token-data = id " " { " " } name " " { " " } ( name | "nil" ) " " { " " } integer " " { " " } integer ;
attribute-data = id " " { " " } name
graph-data = id "--" id
id = (* any single non-whitespace character *) ;
name = id { id } ;
integer = /-?[0-9]+/ ;
```

### File Header

The beginning of a WUAS file consists of zero or more comment lines,
each beginning with a `#` character. These do not affect the image or
JSON output formats and have no semantic meaning, but they will be
preserved if the output format is also `datafile`. These MAY be used
for text configuration, such as Emacs modelines.

After the optional comment section is the version number, as a
positive integer. Zero or more metadata values may follow the version
number. Metadata is an arbitrary key-value store from strings to
arbitrary data and MAY be used for various processing or output
purposes. The meaning of metadata is not defined by this specification
and is dependent upon context.

Version 1 of the datafile format does NOT support metadata.

### Floor Data

The data within a floor is stored in a two-dimensional format that is
difficult to describe in EBNF format. It's most easily seen with an
example.

Versions 1 and 2 of the file format do NOT support multiple floors. In
these formats, only one two-dimensional grid (as specified below) will
be present. These versions should NOT contain a line specifying the
floor number.

If multiple floors are present, then each floor must have a unique
integer identifier.

```
+----------+----------+----------+
| sky      | altar    | sky      |
|          |          |          |
+----------+----------+----------+
| sky      | neutral  | sky      |
|          | &A       |          |
+----------+----------+----------+
| sky      | start    | sky!     |
|          | xy       |          |
+----------+----------+----------+
```

This floor specification defines a 3x3 floor. The left and right edges
are all spaces with name "sky". The middle row consists of three
different spaces. The start space contains two tokens: "x" and "y".
These MUST be keys in the token data table in the footer section. The
neutral space is labeled "A". Finally, the lower-right sky space has
an attribute "!", which MUST likewise be defined in the attribute data
section of the footer.

Space information is placed in boxes with `+` as the corner, as well
as `|` and `-` for the borders. The width of the box is not fixed, but
it MUST be consistent within a single file. The height of the box MUST
always be 2. Within a box, the first line is the space specification
and the second line is the token specification.

The space specification consists of a space name, which MUST be a
sequence of alphanumeric characters. The space name may optionally be
followed by zero or more attribute specifiers, which MUST NOT be
alphanumeric. Every attribute specifier MUST be defined by the
attributes table in the footer section. The meaning of the
alphanumeric space name is not present in the WUAS datafile itself and
is dependent upon the JSON definitions file.

Versions 1 and 2 of the datafile format parse the space specification
line differently. In these versions, the space name itself may be any
sequence of non-whitespace characters other than `*` and `?`. The
space name is then followed by zero or more `*` or `?` characters.
Note that these are /not/ attributes, as Versions 1 and 2 do not
support attributes. These are stripped from the file and NOT preserved
in datafile outputs. The `*` and `?` characters were originally used
for hidden tokens in the datafile format. Starting in Version 5,
/hidden tokens/ should be used to accomplish this goal instead.

The token specification consists of zero or more alphanumeric
characters, where each character is a token identifier defined in the
token section in the footer.

In Versions 4 and above of the datafile format, the token
specification may also contain at most one label. A label is an
ampersand followed by any character. Labels are used to uniquely
identify a space, usually for the graph section in the footer, and
must be globally unique across the file if present.

### File Footer

The footer consists of three sections.

First, each token specified in the board must be defined. A token
definition conists of the token's one-character ID, followed by its
name, its item name, and its X and Y coordinates within the space.

The token's name determines its image and, often, certain behaviors of
the token with respect to various processors. The token's item name,
if present, overrides the token's description. If the token has no
item name, then the "item name" field should be the literal string
`nil`.

On Version 5 of the datafile format and later, a token whose token
name ends with the string `_HIDDEN` will be hidden from the JSON and
image output formats but will be preserved in the datafile format.
That is, it will be hidden from players. A hidden token is not
required to exist in the JSON definitions file. The item name of a
hidden token MUST be `nil`, and its position MUST be `0 0`.

Attribute specifiers consist of the attribute's non-alphanumeric
one-character ID, followed by its name. The meaning of the name is
dependent on the JSON definitions file. The attribute section is only
supported in Versions 3 and newer of the file format.

The graph section defines additional lines that will be drawn atop the
game board as a "highway". The graph's nodes are the labeled spaces in
the spaces section, and the edges are specified in this section. A
single graph edge MUST NOT connect two labeled spaces on different
floors. The graph section is only supported in Versions 4 and newer of
the file format.

## Version History

### Version 5

* Added ability to mark tokens as hidden.

### Version 4

* Added ability to label spaces with a unique one-character name.
* Added graph edge section to file footer.

### Version 3

* Added ability to define multiple floors.
* Added attributes section.
* Removed old-style pseudo-attributes `*` and `?`.

### Version 2

* Added support for arbitrary global metadata fields in the file
  header.

### Version 1

Initial version of the file format, dating back to the original
renderer script.
