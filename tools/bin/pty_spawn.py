#!/usr/bin/env python3

import os
import sys
import pty

sys.exit(os.WEXITSTATUS(pty.spawn(sys.argv[1:])))
