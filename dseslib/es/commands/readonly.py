
import sys

from ..utils import indices


def change_status():
    result = indices.reset_readonly_hot_indices()
    for date in sorted(result.keys()):
        print("acknowledged: {} ({})".format(result[date], date))


def show_current_status():
    blocked = indices.get_readonly_hot_indices()
    if len(blocked) == 0:
        print("No blocked indices found in hot nodes")
        return

    for index in sorted(blocked.keys()):
        print("{}: {}".format(index, " ".join(blocked[index])))


def execute(args):
    if args.reset:
        change_status()
    else:
        show_current_status()
