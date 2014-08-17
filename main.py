#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path

from interpreter import interp

if __name__ == "__main__":
    start_dir = os.path.dirname(__file__)

    # interp.start(os.path.join(start_dir, "test/oop.py"))
    # interp.start(os.path.join(start_dir, "test/2.py"))
    interp.start(os.path.join(start_dir, "test/1.py"))
