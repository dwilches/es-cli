
from typing import NamedTuple


class EsShard(NamedTuple):
    node: str
    index: str
    shard_type: str
    num_shard: int
    size: str
    status: str
    extra: str


class SummarizedShards(NamedTuple):
    node: str
    size: str
    amount: int
