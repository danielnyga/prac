from __future__ import print_function
from argparse import ArgumentParser

from prac import PRAC
from prac.db.ies.extraction import find_frames

prac = PRAC()


command_line = ArgumentParser()
command_line.add_argument('--actioncore', nargs=1, type=str)
command_line.add_argument('--actionroles', nargs='*', type=str, default={})
command_line.add_argument('--sim', type=float)


def parse_roles(*rolestr):
    return dict([s.split(':') for s in rolestr])


if __name__ == '__main__':
    args = command_line.parse_args()
    frames = find_frames(prac, args.actioncore[0], parse_roles(*args.actionroles), similarity=args.sim)
    for frame, sim in frames:
        print('~', sim, frame)
