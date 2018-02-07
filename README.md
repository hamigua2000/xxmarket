# xxmarket
Generate stock markets for 18xx games.

## What is it?

`xxmarket.py` is a Python3 command-line program that, given an in file
in JSON format, creates a Postscript file containing both useful and
essential charts for playing an 18XX railroad game. These charts
include a 2-dimensional stock market (Market), an area for stocks
owned by the bank (Bank Pool), a chart of par values (Par Chart), an
area to indicate the type of the current round (Round Tracker), and an
area to keep track of each company's current earnings per share
(Revenue Tracker).

## Philosophy

`xxmarket` is meant to be a non-interactive tool that is driven by
plain text data. There is no graphical user interface to learn, no
repetitive mousing, no WYSIWYG. To this end, *ALL* configuration data
for the output is contained in the JSON input file. If you want to
change the paper size or orientation, the colors of anything, the
sizes of the cells, the fonts, etc., etc., etc., then you can do so by
editing the JSON input file.

The intended work-flow is

1. Futz with JSON input file.
2. Run `xxmarket.py` and generate output.
3. Decide whether the output is suitable for your purposes. If it is,
then you are done; if it is not, then go to step 1.

The JSON file is meant to be self-documenting. There are comments in
these files in the form of key/value pairs of the form
```
"_comment_": "Comment text",
```
(This is a hack, as JSON does not support comments.)



## System prerequisites.

   `xxmarket.py` is developed and has full support on the GNU-Linux
platform. If you have Python3 running on another platform, it might
should work fine, but no guarantees.

### Required

Python3.

(Actually, the script could be fairly easily modified to support
Python2, and while I've already drunk the Python3 Kool-Aid, you are
certainly free to modify it and go that route if you want.)

### Optional

- A document viewer that supports Postscript (e.g., `evince`).

- If you want to convert your output to PDF, you'll need a Postscript
to PDF converter (e.g., `ps2pdf`, which is standard on most Linux
distributions).

- If you have access to the Linux `poster` program, there is nascent
pseudo-support for tiling output.


## How do I use it?

The basic idea is to create an appropriate JSON file describing the
parameters of your market, and then to call `xxmarket.py` (note: be
sure that the file `xxmarket.py` has execute permissions) with said
file as its primary argument. There are a number of switches and
options that can be viewed by running `xxmarket.py -h`. Rather than
give exhaustive descriptions here, we give a few examples.

### Example 1: default usage

If we simply give a JSON data file:

```
$ ./xxmarket.py 1889.json
```

we get some potentially useful output written to `stdout`:

```
Input file: 1889.json
Output file: 1889.ps
Size of market_cell          : 17.0mm x 18.7mm
Size of bank_pool            : 70.0mm x 145.9mm
Size of par_chart            : 24.0mm x 120.7mm
Size of round_tracker        : 17.0mm x 85.6mm
Size of round_tracker_cell   : 17.0mm x 17.0mm
Size of revenue_tracker_cell : 14.9mm x 19.6mm
```

and a two page output file `1889.ps`. Here is the output, converted to
PNG (with the `convert` command line tool, which is part of
ImageMagick):

![1889 Stock Market and others](images/1889-0.png?raw=true "Market+")

![Revenue Tracker](images/1889-1.png?raw=true "RevTracker")



### Example 2: Eliminating some elements

Here we add a few switches, using their long descriptive form:

```
$ ./xxmarket.py --no_round_tracker --no_revenue_tracker 1889.json
Output file: 1889.ps
Size of market_cell          : 17.0mm x 18.7mm
Size of bank_pool            : 70.0mm x 145.9mm
Size of par_chart            : 24.0mm x 120.7mm
```

And here is a PNG version of the output:

![1889 Stock Market and others](images/1889_less_stuff.png?raw=true "Market-")

## Innards (if I only had a brain)

`xxmarket.py` is not a very clever program. It is entirely possible to
create input files which produce output files that have overlapping or
poorly placed elements, or which cause the program to barf when it
cannot fit the elements onto the canvas (in which case you might want
to futz with the canvas size). Little to no effort was expended for
aesthetics, both in the output and in the code itself. Nonetheless, at
this point it does what I want it to do, and I have the hubris to
believe that one or two other people might find it useful.

I welcome any suggestions; low-hanging fruit has a higher probability
of being implemented. Suggestions with merge patches have a higher
probability of being implemented. Requests for ponies will be ignored.


## The input file format (and grandiose plans)

All parameters for the output are listed in or determined by the input
file, which is written in JSON (Java Script Object Notation). The
provided files, `1830.json` and `1889.json` are meant to be
self-documenting, and should be easy to use as templates for markets
for other 18xx games.

As the program is in an early stage of development, this format is
subject to change. The master branch will change less often, but any
branch will have appropriate templates. If/when the format stabilizes,
and if there are no legal issues, more templates could be added to the
repository.