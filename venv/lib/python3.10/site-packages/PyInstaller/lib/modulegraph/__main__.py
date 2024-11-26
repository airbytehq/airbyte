import sys
import os
import argparse
from .modulegraph import ModuleGraph


def parse_arguments():
    parser = argparse.ArgumentParser(
        conflict_handler='resolve', prog='%s -mmodulegraph' % (
            os.path.basename(sys.executable)))
    parser.add_argument(
        '-d', action='count', dest='debug', default=1,
        help='Increase debug level')
    parser.add_argument(
        '-q', action='store_const', dest='debug', const=0,
        help='Clear debug level')
    parser.add_argument(
        '-m', '--modules', action='store_true',
        dest='domods', default=False,
        help='arguments are module names, not script files')
    parser.add_argument(
        '-x', metavar='NAME', action='append', dest='excludes',
        default=[], help='Add NAME to the excludes list')
    parser.add_argument(
        '-p', action='append', metavar='PATH', dest='addpath', default=[],
        help='Add PATH to the module search path')
    parser.add_argument(
        '-g', '--dot', action='store_const', dest='output', const='dot',
        help='Output a .dot graph')
    parser.add_argument(
        '-h', '--html', action='store_const',
        dest='output', const='html', help='Output a HTML file')
    parser.add_argument(
        'scripts', metavar='SCRIPT', nargs='+', help='scripts to analyse')

    opts = parser.parse_args()
    return opts


def create_graph(scripts, domods, debuglevel, excludes, path_extras):
    # Set the path based on sys.path and the script directory
    path = sys.path[:]

    if domods:
        del path[0]
    else:
        path[0] = os.path.dirname(scripts[0])

    path = path_extras + path
    if debuglevel > 1:
        print("path:", file=sys.stderr)
        for item in path:
            print("   ", repr(item), file=sys.stderr)

    # Create the module finder and turn its crank
    mf = ModuleGraph(path, excludes=excludes, debug=debuglevel)
    for arg in scripts:
        if domods:
            if arg[-2:] == '.*':
                mf.import_hook(arg[:-2], None, ["*"])
            else:
                mf.import_hook(arg)
        else:
            mf.add_script(arg)
    return mf


def output_graph(output_format, mf):
    if output_format == 'dot':
        mf.graphreport()
    elif output_format == 'html':
        mf.create_xref()
    else:
        mf.report()


def main():
    opts = parse_arguments()
    mf = create_graph(
        opts.scripts, opts.domods, opts.debug,
        opts.excludes, opts.addpath)
    output_graph(opts.output, mf)


if __name__ == '__main__':  # pragma: no cover
    try:
        main()
    except KeyboardInterrupt:
        print("\n[interrupt]")
