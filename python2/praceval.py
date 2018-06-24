import argparse
import json
import os
import traceback
from pprint import pformat

from dnutils import logs, out

from prac import PRAC
from prac.core.inference import PRACInference
from prac.db.ies.models import toplan, Worldmodel

parser = argparse.ArgumentParser()
parser.add_argument('--batch', '-b', nargs='+', dest='batch', default=None,
                    help='Import a list of howtos in batch processing whose filenames are given the respective howto '
                         'title, e.g. "Make a pancake." The file content must then be given by the single instruction '
                         'steps, one by line.')
parser.add_argument('--recursive', '-r', action='store_true', dest='recursive', default=False,
                    help='Apply the import of instructions recursively to subdirectories.')
parser.add_argument("-s", "--sim", default=1, type=float, help="Threshold for the similarity value for plan adaptation")
parser.add_argument('-w', '--world', default=None, type=str, help='Path to the world-model file')


logger = logs.getlogger(__name__)


if __name__ == '__main__':
    args = parser.parse_args()

    prac = PRAC()
    prac.verbose = 0

    # load the world model file if any is given
    if args.world is not None:
        with open(args.world, 'r') as f:
            wm = Worldmodel.fromjson(prac, json.load(f))
        logger.info('loaded world model from %s:' % os.path.abspath(args.world))
        logger.debug(pformat(wm.tojson()))
    else:
        wm = None

    for path in args.batch:
        path = os.path.abspath(path)
        out(path)
        for loc, dirs, files in os.walk(path, followlinks=True):
            out(loc, dirs, files)
            for filename in files:
                out(filename)
                try:
                    if filename == 'result.bson':
                        continue
                    command = ' '.join(filename.split('-'))
                    out(command)
                    out(loc)
                    infer = PRACInference(prac, [command], similarity=args.sim, worldmodel=wm)
                    try:
                        infer.run()
                        result = toplan([s.frame for s in infer.steps()], 'json')
                    except Exception:
                        traceback.print_exc()
                        result = []
                    with open(os.path.join(loc, 'result.bson'), 'w+') as f:
                        json.dump(result, f, indent=2)
                except Exception:
                    traceback.print_exc()
