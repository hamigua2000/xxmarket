#!/usr/bin/env python3
import sys
import json
import subprocess
import os
import glob

PTS_PER_MM = 2.834645

def convert_input_lengths(data):
    Lengths = ['canvas_width', 'canvas_height', 'canvas_margin',
               'bank_pool_width', 'market_max_cell_width',
               'market_max_cell_height', 'object_x_sep', 'object_y_sep',
               'round_tracker_sep', 'revenue_tracker_max_cell_width']
    for ell in Lengths:
        data['{}_pt'.format(ell)] = data['{}_mm'.format(ell)] * PTS_PER_MM

def new_data_length(name, value, unit):
    if unit == 'pt':
        key1 = '{}_pt'.format(name)
        val1 = value
        key2 = '{}_mm'.format(name)
        val2 = value / PTS_PER_MM
    elif unit == 'mm':
        key1 = '{}_mm'.format(name)
        key2 = '{}_pt'.format(name)
        val1 = value
        val2 = value * PTS_PER_MM
    else:
        raise ValueError('Unsupported unit: {}'.format(unit))
    for k, v in [[key1, val1], [key2, val2]]:
        data['{}'.format(k)] = v

def add_header(data, f):
    f.write('%!PS-Adobe-3.0\n\n')
    f.write('%%Pages: 2\n')
    f.write('%%Page: 1 1\n')
    f.write('%%EndComments\n')

def new_page(f):
    f.write('showpage\n')
    f.write('%%Page: 2 2\n')

def add_footer(f):
    f.write('showpage\n')
    f.write('%%EOF\n')

def set_page_size(data, f):
    w = data['canvas_width_pt']
    h = data['canvas_height_pt']
    f.write('<< /PageSize [{:.0f} {:.0f}] >> setpagedevice\n'.format(w, h))

def get_market_cell_color(v, data, i, j):
    ret = 'white'
    for c, vals in data['market_color_by_value'].items():
        if v in vals:
            ret = c
    for c, pos_list in data['market_color_by_position'].items():
        if c == '_comment_':
            continue
        row = i
        if [row, j] in pos_list:
            ret = c
    return ret

def text_at(x, y, text, text_font, text_size):
    ret = ''
    ret += '/{} findfont\n'.format(text_font)
    ret += '{} scalefont\n'.format(text_size)
    ret += 'setfont\n'
    ret += 'newpath {} {} moveto ({}) show\n'.format(x, y, text)
    return ret

def cell_at(x, y, w, h, c='white', t='', t_font='Helvetica', t_size=12):
    """Return Postscript string to draw and label a colored cell.

    x, y -- integer: coordinates of the lower left hand corner.
    w, h -- integer: width and height.
    t -- string: label for the cell.

    t_font -- string: A font supported or findable by a postscript
                      interpreter. The following are standard
                      postscript fonts which should always be
                      available:

                      Times-[Roman,Italic,Bold,BoldItalic],
                      Helvetica, Helvetica-[Oblique,Bold,BoldOblique],
                      Courier, Courier-[Oblique,Bold,BoldOblique],
                      Symbol

    t_size -- integer: vertical size of text in points (1 point=1/72 inch).

    """
    rgb = data['colors'][c]
    r,g,b = (x/255.0 for x in rgb)
    if data['no_color']:
        r, g, b = 1.0, 1.0, 1.0
    ret = ''
    ret += 'gsave\n'
    ret += '{} {} {} setrgbcolor\n'.format(r, g, b)
    ret += 'newpath {} {} {} {} rectfill\n'.format(x, y, w, h)
    ret += 'grestore\n'
    # Place the text at the top interior of the cell, with some
    # breathing space.
    ret += text_at(x+t_size/2, y+h-t_size, t, t_font, t_size)
    # The actual box.
    ret += 'newpath {} {} {} {} rectstroke\n'.format(x, y, w, h)
    return ret

def write_market_cells(f, data):
    # Handy abbreviations.
    w = data['market_cell_width_pt']
    h = data['market_cell_height_pt']
    m = data['canvas_margin_pt']
    fs = data['market_cell_fontsize_pt']
    V = data['market_values']
    n = len(V)
    for i in range(n):
        # Because coordinate 0,0 is in the lower left, and the market rows
        # are listed from top to bottom, we "complement" the y-coordinate.
        y = (n-1-i)*h + m
        row = V[i]
        for j in range(len(row)):
            x = j*w + m
            v = V[i][j]
            t = '{}'.format(v)
            # We only write cells with positive value; value 0 is used
            # to skip a cell.
            if v > 0:
                c = get_market_cell_color(v, data, i, j)
                f.write(cell_at(x, y, w, h, c,
                             t, t_size=fs, t_font=data['font']))

def determine_market_cell_dimensions(data):
    """The width and height data are stored in the data dictionary as
    data['market_cell_[width|height]_[pt|mm]."""
    # Currently, we use the max available area inside the margins.
    pw = data['canvas_width_pt']
    ph = data['canvas_height_pt']
    m = data['canvas_margin_pt']
    w = (pw - 2*m) // max([len(row) for row in data['market_values']])
    h = (ph - 2*m) // len(data['market_values'])
    w = min(w, data['market_max_cell_width_pt'])
    h = min(h, data['market_max_cell_height_pt'])
    new_data_length('market_cell_width', w, 'pt')
    new_data_length('market_cell_height', h, 'pt')

def create_market(data, f):
    determine_market_cell_dimensions(data)
    write_market_cells(f, data)

def get_ledge_height(data, x):
    """Return the y-coordinate of the bottom of the market cell above x."""
    # First find out which column x falls into.
    cell_column = x // data['market_cell_width_pt']
    # Next, we need to know how many rows down before there is a row
    # which has *fewer* than cell_column number of cells.
    n = len(data['market_values'])
    h_c = data['market_cell_height_pt']
    for i in range(n):
        if len(data['market_values'][i]) < cell_column:
            ret = data['canvas_height_pt'] - h_c*i - data['canvas_margin_pt']
            return ret
    raise ValueError('x-coord too far to the left')

def get_row_width(data, y):
    """Return the x-coord of the right side of the market cell left of x."""
    # First find out which row y falls into. Since y is measured from
    # the bottom of the canvas and row index 0 is at the top of the
    # canvas, we need to complement.
    n = len(data['market_values'])
    cell_row = int(y // data['market_cell_height_pt'])
    row = data['market_values'][n - 1 - cell_row]
    # Return the graphic length of the row.
    n = len(row)
    ret = n * data['market_cell_width_pt']
    return ret

def create_bank_pool(data, f):
    """Side effect: store the calculated bank pool dimensions and lower
left hand coordinates in data:

    data['bank_pool_<datum>_<unit>']

    <datum> is one of x, y, width, height, and <unit> is either pt or mm.
    """
    w = data['bank_pool_width_pt']
    # Place so the lower right corner of the Bank Pool is basically
    # the lower right corner of the canvas, with margins.
    x = data['canvas_width_pt'] - w - data['canvas_margin_pt']
    y = data['canvas_margin_pt']
    h_l = get_ledge_height(data, x) - data['object_y_sep_pt']
    h = h_l - data['canvas_margin_pt']
    f.write(cell_at(x, y, w, h, t="Bank Pool", t_font=data['font'], t_size=20))
    # Store calculated values in data dictionary.
    new_data_length('bank_pool_x', x, 'pt')
    new_data_length('bank_pool_y', y, 'pt')
    new_data_length('bank_pool_width', w, 'pt')
    new_data_length('bank_pool_height', h, 'pt')

def create_par_chart(data, f):
    """Side effect: store the lower left hand coordinates in data."""
    # Build the chart to the left of the Bank Pool.
    if not data['no_bank_pool']:
        x0 = data['bank_pool_x_pt']
    else:
        x0 = data['canvas_width_pt'] - data['canvas_margin_pt']
    # Find the width of the widest cell.
    w0 = max([ d['width_mm'] for d in data['par_chart']])
    w0 *= PTS_PER_MM
    data['par_chart_cell_width_pt'] = w0
    x = x0 - data['object_x_sep_pt'] - w0
    y = data['canvas_margin_pt']
    # By using the ledge height we guarantee that the par chart will
    # fit under the market.
    h_l = get_ledge_height(data, x) - data['object_y_sep_pt']
    num_par_values = len(data['par_chart'])
    h = min(h_l/num_par_values, data['market_cell_height_pt'])
    for i in range(num_par_values):
        p = data['par_chart'][i]
        w = p['width_mm']*PTS_PER_MM
        c = p['color']
        f.write(cell_at(x, y, w, h, c, t='{}'.format(p['value'])))
        y += h
    # Label the chart.
    fn = data['font']
    fs = data['par_chart_label_fontsize_pt']
    f.write(text_at(x+fs, y+fs/2, 'PAR', fn, fs))
    # Store the calculated values.
    new_data_length('par_chart_x', x, 'pt')
    new_data_length('par_chart_y', y, 'pt')
    new_data_length('par_chart_width', w, 'pt')
    pch = y - data['canvas_margin_pt'] + 1.5*fs
    new_data_length('par_chart_height', pch, 'pt')

def round_tracker_at(x, y, w, h, sep, fn, fs, orientation='vertical'):
    ret = ''
    for col in ['white', 'yellow', 'green', 'brown']:
        ret += cell_at(x, y, w, h, c=col)
        if orientation == 'vertical':
            y += h + sep
        elif orientation == 'horizontal':
            x -= w + sep
        else:
            raise ValueError("Unknown orientation: {}".format(orientation))
    if orientation == 'horizontal':
        x += w + sep
        y += h + sep
    ret += text_at(x, y, "Round", fn, fs)
    return ret

def create_round_tracker(data, f):
    m = data['canvas_margin_pt']
    c = data['market_cell_width_pt']
    delta = data['round_tracker_sep_pt']
    fn = data['font']
    fs = data['round_tracker_fontsize_pt']
    orient = data['round_tracker_orientation']
    # Build to the left of the Bank Pool or Par Chart if such exist.
    if not data['no_par_chart']:
        x0 = data['par_chart_x_pt']
    elif not data['no_bank_pool']:
        x0 = data['bank_pool_x_pt']
    else:
        x0 = data['canvas_width_pt'] - data['canvas_margin_pt']
    x = x0 - data['object_x_sep_pt'] - c
    y = 0
    w = 0
    w_tot = 0
    h = 0
    h_tot = 0
    if orient == 'vertical':
        y = m
        h_l = get_ledge_height(data, x) - data['object_y_sep_pt']
        w = c
        h = min((h_l - y - 4*delta - fs)/4, c)
        w_tot = w
        h_tot = 4*(h + delta) + fs
    elif orient == 'horizontal':
        # This is still a bit wonky. The y value is not smart or
        # scaling in any way.
        y = m + 2*c
        w_l = get_row_width(data, y)
        w = min((x - w_l - 3*delta)/4, c)
        h = c
        h_tot = h
        w_tot = 4*(h + delta)
    f.write(round_tracker_at(x, y, w, h, delta, fn, fs, orient))
    new_data_length('round_tracker_cell_width', w, 'pt')
    new_data_length('round_tracker_cell_height', h, 'pt')
    new_data_length('round_tracker_width', w_tot, 'pt')
    new_data_length('round_tracker_height', h_tot, 'pt')

def revenue_tracker_at(nrows, ncols, w, h, m,
                       color_default, color_5, color_10, color_100,
                       fn, fs_cell, fs_label):
    ret = ''
    for i in range(nrows):
        y = (nrows-1-i)*h + m
        for j in range(ncols):
            x = j*w + m
            v = i*ncols + j + 1
            t = '{}'.format(v)
            c = color_default
            # This is currently a little sloppy, since 10 is a
            # multiple of 5, we let the logic "fall through" and have
            # the color value overwritten.
            if v % 5 == 0:
                c = color_5
            if v % 10 == 0:
                c = color_10
            if v >= 100:
                c = color_100
                t = '{}'.format(100*(v-100))
            ret += cell_at(x, y, w, h, c, t, t_size=fs_cell, t_font=fn)
    x = m
    y = (nrows)*h + m
    ret += text_at(x+fs_label, y+fs_label/2, 'Revenue', fn, fs_label)
    return ret

def create_revenue_tracker(data, f):
    pw = data['canvas_width_pt']
    ph = data['canvas_height_pt']*data['revenue_tracker_canvas_ratio']
    m = data['canvas_margin_pt']
    nrows = data['revenue_tracker_nrows']
    ncols = data['revenue_tracker_ncols']
    f.write('0 {} translate\n'.format(ph-m-data['revenue_tracker_label_fontsize_pt']))
    w = min((pw - 2*m) / ncols, data['revenue_tracker_max_cell_width_pt'])
    h = (ph - 2*m) / nrows
    new_data_length('revenue_tracker_cell_width', w, 'pt')
    new_data_length('revenue_tracker_cell_height', h, 'pt')
    fn = data['font']
    fs = data['revenue_tracker_cell_fontsize_pt']
    f.write(revenue_tracker_at(nrows, ncols, w, h, m,
                               data['revenue_tracker_default_color'],
                               data['revenue_tracker_5s_color'],
                               data['revenue_tracker_10s_color'],
                               data['revenue_tracker_100s_color'],
                               data['font'],
                               data['revenue_tracker_cell_fontsize_pt'],
                               data['revenue_tracker_label_fontsize_pt']))

def initialize(args):
    import os.path
    root, ext = os.path.splitext(args.input_file)
    with open(args.input_file, 'r') as f:
        data = json.load(f)
    data['input_file'] = args.input_file
    data['output_file'] = "{}.ps".format(root)
    data['ps_output_file'] = "{}.ps".format(root)
    data['file_basename'] = root
    data['no_color'] = args.no_color
    data['no_bank_pool'] = args.no_bank_pool
    data['no_par_chart'] = args.no_par_chart
    return data

def output_pdf(data):
    out_ps = data['ps_output_file']
    subprocess.call(["ps2pdf", out_ps])
    os.unlink(out_ps)

def report(data):
    print("Input file:", data['input_file'])
    print('Output file: {}'.format(data['output_file']))
    if data['no_color']:
        print("Creating a market with no color.")
    for x in ['market_cell', 'bank_pool', 'par_chart', 'round_tracker',
              'round_tracker_cell', 'revenue_tracker_cell']:
        if '{}_width_mm'.format(x) in data:
            w = data['{}_width_mm'.format(x)]
            h = data['{}_height_mm'.format(x)]
            print('Size of {:21}: {:0.1f}mm x {:0.1f}mm'.format(x, w ,h))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Stock market data in JSON format")
    parser.add_argument("-c", "--no_color", help="Remove all color (except black) from output", action="store_true")
    parser.add_argument("-b", "--no_bank_pool", help="Do not include a Bank Pool", action="store_true")
    parser.add_argument("-p", "--no_par_chart",
                        help="Do not include Par Chart", action="store_true")
    parser.add_argument("-r", "--no_round_tracker",
                        help="Do not include Round Tracker", action="store_true")
    parser.add_argument("-t", "--no_revenue_tracker",
                        help="Do not include Revenue Tracker on separate page",
                        action="store_true")
    parser.add_argument("-m", "--no_market",
                        help="Do not include a Market", action="store_true")
    parser.add_argument("-P", "--output_pdf",
                        help="Output PDF file instead of Postscript",
                        action="store_true")
    parser.add_argument("-S", "--tile_output_ps",
                        help="Tile output (requires linux poster program)",
                        action="store_true")
    args = parser.parse_args()
    data = initialize(args)
    convert_input_lengths(data)
    with open(data['ps_output_file'], 'w') as f:
        add_header(data, f)
        set_page_size(data, f)
        if not args.no_market:
            create_market(data, f)
        if not args.no_bank_pool:
            create_bank_pool(data, f)
        if not args.no_par_chart:
            create_par_chart(data, f)
        if not args.no_round_tracker:
            create_round_tracker(data, f)
        if not args.no_revenue_tracker:
            new_page(f)
            create_revenue_tracker(data, f)
        add_footer(f)
    if args.output_pdf:
        data['output_file'] = '{}.pdf'.format(data['file_basename'])
        output_pdf(data)
    if args.tile_output_ps:
        box ='{}x{}mm'.format(data['canvas_width_mm'],
                              data['canvas_height_mm'])
        scale_factor = 1.27     # Need to pass or calculate this.
        paper_size = 'Letter'
        ps_tiled_output_file = '{}_s{}_tiled.ps'.format(data['file_basename'], scale_factor)
        subprocess.call(['poster', '-i', '{}'.format(box),
                         '-s', '{}'.format(scale_factor),
                         '-m', '{}'.format(paper_size),
                         '-o', '{}'.format(ps_tiled_output_file),
                         data['ps_output_file']])
        print('Tiled output file: {}'.format(ps_tiled_output_file))
    report(data)
