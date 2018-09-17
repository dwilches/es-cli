
from enum import Flag, auto


class NodeType(Flag):
    HOT = auto()
    WARM = auto()
    PERCOLATE = auto()
