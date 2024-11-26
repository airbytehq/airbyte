# -----------------------------------------------------------------------------
# Copyright (c) 2005-2020, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
# -----------------------------------------------------------------------------

# Enchant hook test. Tested with PyEnchant 1.6.6.

import sys
import enchant

print(80 * '-')
print('PYTHONPATH: %s' % sys.path)

# At least one backend should be available
backends = [x.name for x in enchant.Broker().describe()]
if len(backends) < 1:
    raise SystemExit('Error: No dictionary backend available')
print(80 * '-')
print('Backends: ' + ', '.join(backends))

# Usually en_US dictionary should be bundled.
languages = enchant.list_languages()
dicts = [x[0] for x in enchant.list_dicts()]
if len(dicts) < 1:
    raise SystemExit('No dictionary available')
print(80 * '-')
print('Languages: %s' % ', '.join(languages))
print('Dictionaries: %s' % dicts)
print(80 * '-')

# Try spell checking if English is availale
language = 'en_US'
if language in languages:
    d = enchant.Dict(language)
    print('d.check("hallo") %s' % d.check('hallo'))
    print('d.check("halllo") %s' % d.check('halllo'))
    print('d.suggest("halllo") %s' % d.suggest('halllo'))
