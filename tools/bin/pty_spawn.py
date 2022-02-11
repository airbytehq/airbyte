#!/usr/bin/env python3

import sys
import pty

pty.spawn(sys.argv[1:])
