#!/usr/bin/env python3

import doctest

import coliprot


if __name__ == "__main__":
    (f, t) = doctest.testmod(coliprot)
    failures = f
    tests = t

    if failures == 0:
        print("All %d tests successfully passed." % tests)
    else:
        exit(1)
