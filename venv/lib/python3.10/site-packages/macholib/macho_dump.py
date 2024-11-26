#!/usr/bin/env python

from __future__ import print_function

import sys

from macholib._cmdline import main as _main
from macholib.mach_o import CPU_TYPE_NAMES, MH_CIGAM_64, MH_MAGIC_64, get_cpu_subtype
from macholib.MachO import MachO

ARCH_MAP = {
    ("<", "64-bit"): "x86_64",
    ("<", "32-bit"): "i386",
    (">", "64-bit"): "ppc64",
    (">", "32-bit"): "ppc",
}


def print_file(fp, path):
    print(path, file=fp)
    m = MachO(path)
    for header in m.headers:
        seen = set()

        if header.MH_MAGIC == MH_MAGIC_64 or header.MH_MAGIC == MH_CIGAM_64:
            sz = "64-bit"
        else:
            sz = "32-bit"

        arch = CPU_TYPE_NAMES.get(header.header.cputype, header.header.cputype)

        subarch = get_cpu_subtype(header.header.cputype, header.header.cpusubtype)

        print(
            "    [%s endian=%r size=%r arch=%r subarch=%r]"
            % (header.__class__.__name__, header.endian, sz, arch, subarch),
            file=fp,
        )
        for _idx, _name, other in header.walkRelocatables():
            if other not in seen:
                seen.add(other)
                print("\t" + other, file=fp)
    print("", file=fp)


def main():
    print(
        "WARNING: 'macho_dump' is deprecated, use 'python -mmacholib dump' " "instead"
    )
    _main(print_file)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
