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
Nothing else comes to mind. Actually, the script could be fairly
easily modified to support Python2, and while I've already drunk the
Python3 Kool-Aid, you are certainly free to go that route if you want.

## How do I use it?

The basic idea is to create an appropriate JSON file describing the
parameters of your market, and then to call `xxmarket.py` with said
file as its primary argument. There are a number of switches and
options that can be viewed by running `xxmarket.py -h`. Rather than
give exhaustive descriptions here, we give a few examples.

(Note: be sure that the file `xxmarket.py` has execute permissions.)

```
$ ./xxmarket.py 1830.json
```