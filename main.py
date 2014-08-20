#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path

from interpreter import Interpreter

if __name__ == "__main__":
    start_dir = os.path.dirname(__file__)

    # Interpreter.instance().start("test/oop.py")
    # Interpreter.instance().start("test/2.py")
    Interpreter.instance().start("test/1.py")

