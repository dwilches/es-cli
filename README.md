# es-cli
Command line utility to manage ElasticSearch

We created this utility to avoid writing `curl` to manage our [ElasticSearch](https://www.elastic.co) cluster, as it was error prone and it was hard to ensure our command was wellformed before executing it. With this utility, we are sure we are executing proven commands each time.

The following commonly used operations are supported. If you have recommendations for new features, please create an [Issue](/DefenseStorm/es-cli/issues):

- [`es allocation`](#allocation)
- [`es durability`](#durability)
- [`es move-shards`](#moving-shards)
- [`es read-only`](#read-only-indices)
- [`es shards`](#listing-shards)


# Allocation

Controls the value of the ES property: [`cluster.routing.allocation.enable`](https://www.elastic.co/guide/en/elasticsearch/reference/current/shards-allocation.html).

> Shard allocation is the process of allocating shards to nodes. This can happen during initial recovery, replica allocation, rebalancing, or when nodes are added or removed.
> 
>  - **all**: allows shard allocation for all kinds of shards.
>  - **none**: no shard allocations of any kind are allowed for any indices.

#### Find out the current allocation value

```
$ es allocation
all
```

#### Disable allocation
```
$ es allocation --disable
acknowledged: True
allocation: none
```

#### Enable allocation
```
$ es allocation --enable
acknowledged: True
allocation: all
```


# Durability

Controls the value of the ES property: [`index.translog.durability`](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules-translog.html#_translog_settings).

> Whether or not to fsync and commit the translog after every index, delete, update, or bulk request. This setting accepts the following parameters:
> - **request:** (default) fsync and commit after every request. In the event of hardware failure, all acknowledged writes will already have been committed to disk.
> - **async:** fsync and commit in the background every sync_interval. In the event of hardware failure, all acknowledged writes since the last automatic commit will be discarded.

#### Find out the durability setting for today's indices
```
$ es durability
company-name-ccccccccccccccccc-2018-10-20: request
company-name-bbbbbbbbbbbbbbbbb-2018-10-20: request
company-name-aaaaaaaaaaaaaaaaa-2018-10-20: request
```

#### Find out the durability setting for another day's indices
```$ es durability --date 2018-10-19
company-name-ccccccccccccccccc-2018-10-19: default
company-name-bbbbbbbbbbbbbbbbb-2018-10-19: default
company-name-aaaaaaaaaaaaaaaaa-2018-10-19: default
```

#### Change durability to async
```
$ es durability  --async
acknowledged: True
company-name-ccccccccccccccccc-2018-10-20: async
company-name-bbbbbbbbbbbbbbbbb-2018-10-20: async
company-name-aaaaaaaaaaaaaaaaa-2018-10-20: async
```

#### Change durability to request
```
$ es durability  --request
acknowledged: True
company-name-ccccccccccccccccc-2018-10-20: request
company-name-bbbbbbbbbbbbbbbbb-2018-10-20: request
company-name-aaaaaaaaaaaaaaaaa-2018-10-20: request
```

# Read-only indices

#### Listing read-only indices in hot nodes

All indices in hot nodes should be read-write in normal operation, but if ES is running low on disk space and it reaches the ["flood stage watermark"](https://www.elastic.co/guide/en/elasticsearch/reference/current/disk-allocator.html), it will make the indices read-only. To find out if any index is in that state, execute `es read-only`:

```
$ es read-only
No blocked indices found in hot nodes
```

```
$ es read-only
company-name-ccccccccccccccccc-2018-10-20: read_only_allow_delete
```

#### Making indices in hot nodes read-write

```
$ es read-only --reset
acknowledged: True (2018-10-22)
acknowledged: True (2018-10-23)
acknowledged: True (2018-10-24)
```



# Listing shards

#### Listing detailed info of shards in hot nodes
```
$ es shards
INDEX                                       NUM     SIZE    NODE                                    STATUS
company-name-aaaaaaaaaaaaaaaaa-2018-10-20   0       35mb    environ-data-hot-xxxxxxxxxxxxxxxxx       STARTED
company-name-aaaaaaaaaaaaaaaaa-2018-10-20   0       35mb    environ-data-hot-yyyyyyyyyyyyyyyyy       STARTED
company-name-bbbbbbbbbbbbbbbbb-2018-10-20   1       35mb    environ-data-hot-xxxxxxxxxxxxxxxxx       STARTED
company-name-bbbbbbbbbbbbbbbbb-2018-10-20   1       35mb    environ-data-hot-zzzzzzzzzzzzzzzzz       STARTED
company-name-bbbbbbbbbbbbbbbbb-2018-10-20   3       35mb    environ-data-hot-xxxxxxxxxxxxxxxxx       STARTED
company-name-bbbbbbbbbbbbbbbbb-2018-10-20   3       35mb    environ-data-hot-yyyyyyyyyyyyyyyyy       STARTED
company-name-bbbbbbbbbbbbbbbbb-2018-10-20   2       35mb    environ-data-hot-zzzzzzzzzzzzzzzzz       STARTED
company-name-bbbbbbbbbbbbbbbbb-2018-10-20   2       35mb    environ-data-hot-yyyyyyyyyyyyyyyyy       STARTED
company-name-bbbbbbbbbbbbbbbbb-2018-10-20   4       35mb    environ-data-hot-xxxxxxxxxxxxxxxxx       STARTED
company-name-bbbbbbbbbbbbbbbbb-2018-10-20   4       35mb    environ-data-hot-zzzzzzzzzzzzzzzzz       STARTED
company-name-bbbbbbbbbbbbbbbbb-2018-10-20   0       35mb    environ-data-hot-xxxxxxxxxxxxxxxxx       STARTED
```

#### Summarizing distribution of shards per node
```
$ es shards -s
NODE NAME                                       NUM     SIZE
environ-data-hot-zzzzzzzzzzzzzzzzz               99      35gb
environ-data-hot-xxxxxxxxxxxxxxxxx               98      35gb
environ-data-hot-yyyyyyyyyyyyyyyyy               98      35gb
```


# Moving shards

This command gives you information about which shards to move (it doesn't move the shards itself).

#### Moving shards away from busy nodes

```
$ es move-shards --from environ-data-hot-ddddddddddddddddd
The node environ-data-hot-ddddddddddddddddd from where you want to move shards has 80 shards (500gb).
        * company-name-eeeeeeeeeeeeeeeeee-2018-10-24 1 (23mb)
        * company-name-iiiiiiiiiiiiiiiiii-2018-10-24 1 (23mb)
        * company-name-jjjjjjjjjjjjjjjjjj-2018-10-24 1 (23mb)
          ...
        * company-name-kkkkkkkkkkkkkkkkkk-2018-10-21 0 (13gb)
        * company-name-pppppppppppppppppp-2018-10-21 0 (12gb)
        * company-name-hhhhhhhhhhhhhhhhhh-2018-10-21 1 (33gb)

From the nodes in the same AZ, these are the 3 with fewer shards:
        * environ-data-hot-xxxxxxxxxxxxxxxx1: 67 shards (31gb)
        * environ-data-hot-xxxxxxxxxxxxxxxx3: 69 shards (32gb)
        * environ-data-hot-xxxxxxxxxxxxxxxx2: 70 shards (32gb)

From the nodes in the same AZ, these are the 3 with smaller shards:
        * environ-data-hot-xxxxxxxxxxxxxxxx1: 67 shards (31gb)
        * environ-data-hot-xxxxxxxxxxxxxxxx2: 70 shards (32gb)
        * environ-data-hot-xxxxxxxxxxxxxxxx3: 69 shards (32gb)
```

#### Moving shards into idle nodes

```
$ es move-shards --to environ-data-hot-ddddddddddddddddd
The node to which you want to move shards has 70 shards (29gb).

From the nodes in the same AZ, these are the 3 with more shards:
        * environ-data-hot-vvvvvvvvvvvvvvvvvv: 90 shards (500gb)
                * company-name-ffffffffffffffffff-2018-10-21 0 (27gb)
                * company-name-hhhhhhhhhhhhhhhhhh-2018-10-22 3 (26gb)
                * company-name-mmmmmmmmmmmmmmmmmm-2018-10-22 1 (25gb)
                  ...
                * company-name-gggggggggggggggggg-2018-10-24 0 (23mb)
                * company-name-ffffffffffffffffff-2018-10-24 0 (23mb)
                * company-name-eeeeeeeeeeeeeeeeee-2018-10-24 2 (23mb)

        * environ-data-hot-wwwwwwwwwwwwwwwww: 90 shards (500gb)
                * company-name-llllllllllllllllll-2018-10-22 1 (39gb)
                * company-name-oooooooooooooooooo-2018-10-22 0 (33gb)
                * company-name-mmmmmmmmmmmmmmmmmm-2018-10-21 0 (23gb)
                  ...
                * company-name-pppppppppppppppppp-2018-10-24 4 (23mb)
                * company-name-qqqqqqqqqqqqqqqqqq-2018-10-24 0 (23mb)
                * company-name-rrrrrrrrrrrrrrrrrr-2018-10-24 2 (23mb)

        * environ-data-hot-xaxaxaxaxaxaxaxaxa: 89 shards (500gb)
                * company-name-ssssssssssssssssss-2018-10-21 3 (25gb)
                * company-name-ssssssssssssssssss-2018-10-21 2 (23gb)
                * company-name-gggggggggggggggggg-2018-10-21 0 (20gb)
                  ...
                * company-name-tttttttttttttttttt-2018-10-24 2 (23mb)
                * company-name-uuuuuuuuuuuuuuuuuu-2018-10-24 0 (23mb)
                * company-name-rrrrrrrrrrrrrrrrrr-2018-10-24 1 (23mb)

From the nodes in the same AZ, these are the 3 with larger shards:
        * environ-data-hot-vvvvvvvvvvvvvvvvvvv: 90 shards (500gb)
                * company-name-ffffffffffffffffff-2018-10-21 0 (27gb)
                * company-name-hhhhhhhhhhhhhhhhhh-2018-10-22 3 (26gb)
                * company-name-mmmmmmmmmmmmmmmmmm-2018-10-22 1 (25gb)
                  ...
                * company-name-gggggggggggggggggg-2018-10-24 0 (23mb)
                * company-name-ffffffffffffffffff-2018-10-24 0 (23mb)
                * company-name-eeeeeeeeeeeeeeeeee-2018-10-24 2 (23mb)

        * environ-data-hot-yayayayayayayaya: 79 shards (500gb)
                * company-name-ssssssssssssssssss-2018-10-21 3 (25gb)
                * company-name-ssssssssssssssssss-2018-10-21 2 (23gb)
                * company-name-gggggggggggggggggg-2018-10-21 0 (20gb)
                  ...
                * company-name-tttttttttttttttttt-2018-10-24 2 (23mb)
                * company-name-uuuuuuuuuuuuuuuuuu-2018-10-24 0 (23mb)
                * company-name-rrrrrrrrrrrrrrrrrr-2018-10-24 1 (23mb)

        * environ-data-hot-zazazazazazazaza: 80 shards (500gb)
                * company-name-pppppppppppppppppp-2018-10-22 1 (39gb)
                * company-name-oooooooooooooooooo-2018-10-22 0 (33gb)
                * company-name-mmmmmmmmmmmmmmmmmm-2018-10-21 0 (23gb)
                  ...
                * company-name-pppppppppppppppppp-2018-10-24 4 (23mb)
                * company-name-qqqqqqqqqqqqqqqqqq-2018-10-24 0 (23mb)
                * company-name-rrrrrrrrrrrrrrrrrr-2018-10-24 2 (23mb)
```


# Getting help

Execute `es -h` to see the available subcommands:
```
$ es -h
usage: es [-h]
          {allocation,durability,move-shards,read-only,shards,version} ...

Executes common commands against ES so you need to craft fewer curls.

positional arguments:
  {allocation,durability,move-shards,read-only,shards,version}
    allocation          gets/sets the allocation policy of the cluster
    durability          gets/sets the durability of all of today's indices
    move-shards         helping hand for manually moving shards
    read-only           lists read-only indices in hot nodes
    shards              lists shards in hot nodes
    version             print eslib's version

optional arguments:
  -h, --help            show this help message and exit
```
Execute `es <subcommand> -h` to see detailed subcommand help:
```
$ es allocation -h
usage: es allocation [-h] [--show | --enable | --disable]

optional arguments:
  -h, --help         show this help message and exit
  --show             shows the current setting for the cluster's allocation
                     (default)
  --enable, --all    enables allocation for the cluster
  --disable, --none  disables allocation for the cluster
```
