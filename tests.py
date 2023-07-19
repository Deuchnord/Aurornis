#!/usr/bin/env python3

import doctest
import aurornis
import warnings


if __name__ == "__main__":
    warnings.filterwarnings("default", category=DeprecationWarning)

    (f, t) = doctest.testmod(aurornis)
    failures = f
    tests = t

    if failures == 0:
        print("All %d tests successfully passed." % tests)
    else:
        exit(1)
