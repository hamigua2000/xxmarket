# xxmarket
Generate stock markets for 18xx games.

## What is it?

`xxmarket.py` is a Python3 program that, given a data file in JSON
format, creates a Postscript file containing both useful and essential
charts for playing 18XX railroad games. These charts include a
2-dimensional stock market, an area for stocks owned by the bank, a
chart of par values, a round tracker, and a revenue tracker.

## System prerequisites.

Python3. A document viewer that supports Postscript (e.g., `evince`).
A Postscript to PDF converter (e.g., `ps2pdf`) if you want to convert
your output to PDF. Nothing else comes to mind.

Actually, the script could be fairly easily modified to support
Python2, and while I've already drunk the Python3 Kool-Aid, you are
certainly free to modify it and go that route if you want.

## How do I use it?

The basic idea is to create an appropriate JSON file describing the
parameters of your market, and then to call `xxmarket.py` (Note: be
sure that the file `xxmarket.py` has execute permissions) with said
file as its primary argument. There are a number of switches and
options that can be viewed by running `xxmarket.py -h`. Rather than
give exhaustive descriptions here, we give a few examples.

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
PDF:

![1889 Stock Market and others](images/1889.pdf?raw=true "Title")
