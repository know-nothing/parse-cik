import os


def from_tsv(filename_in):
    with open(filename_in, 'r') as f:
        return [[os.path.dirname(filename_in), filename_in] + _l.split('\t') for _l in f.readlines()]


def transpose(arr_in):
    return [list(x) for x in zip(*arr_in)]


def transpose_with_header(arr_in):
    arr = transpose(arr_in)
    return arr[0], arr[1:]
