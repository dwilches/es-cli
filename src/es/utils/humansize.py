
import re

_units = {'b': 1, 'kb': 1024, 'mb': 1024*1024, 'gb': 1024*1024*1024}
_re_size = re.compile(r"(?P<value>[\d.]+)(?P<unit>\S*)")


def parse(human_size):
    match = _re_size.match(human_size)
    if not match:
        print('Invalid shard size found: {}'.format(human_size))
        return 0

    value = float(match.group('value'))
    unit = match.group('unit')

    if unit not in _units:
        print('Invalid unit found ({}): {}'.format(unit, human_size))
        return 0

    return value * _units[unit]


def stringify(size):
    desired_unit = 'b'
    for unit in ['kb', 'mb', 'gb']:
        if _units[unit] < size:
            desired_unit = unit
    return "{0:.2f}{1}".format(size / _units[desired_unit], desired_unit)
