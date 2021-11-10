#!/usr/bin/env python3

import doctest
import aurornis


if __name__ == "__main__":
    (f, t) = doctest.testmod(aurornis)
    failures = f
    tests = t

    if failures == 0:
        print("All %d tests successfully passed." % tests)
    else:
        exit(1)
