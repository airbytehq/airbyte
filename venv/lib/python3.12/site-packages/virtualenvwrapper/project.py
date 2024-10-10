# encoding: utf-8
#
# Copyright (c) 2010 Doug Hellmann.  All rights reserved.
#
"""virtualenvwrapper.project
"""

import logging
import os

from virtualenvwrapper.user_scripts import PERMISSIONS, make_hook, run_global

log = logging.getLogger(__name__)

GLOBAL_HOOKS = [
    # mkproject
    ("premkproject",
     "This hook is run after a new project is created "
     "and before it is activated.",
     PERMISSIONS),
    ("postmkproject",
     "This hook is run after a new project is activated.",
     PERMISSIONS),
]


def initialize(args):
    """Set up user hooks
    """
    for filename, comment, permissions in GLOBAL_HOOKS:
        make_hook(os.path.join('$VIRTUALENVWRAPPER_HOOK_DIR', filename),
                  comment, permissions)
    return


def pre_mkproject(args):
    log.debug('pre_mkproject %s', str(args))
    run_global('premkproject', *args)
    return


def post_mkproject_source(args):
    return """
#
# Run user-provided scripts
#
[ -f "$VIRTUALENVWRAPPER_HOOK_DIR/postmkproject" ] && \
    source "$VIRTUALENVWRAPPER_HOOK_DIR/postmkproject"
"""


def post_activate_source(args):
    return """
#
# Change to the project directory, as long as we haven't been told not to.
#
[ -f "$VIRTUAL_ENV/$VIRTUALENVWRAPPER_PROJECT_FILENAME" \
  -a "$VIRTUALENVWRAPPER_PROJECT_CD" = 1 ] && \
    virtualenvwrapper_cd \
        "$(cat \"$VIRTUAL_ENV/$VIRTUALENVWRAPPER_PROJECT_FILENAME\")"
if [ -f "$VIRTUAL_ENV/$VIRTUALENVWRAPPER_PROJECT_FILENAME" ]; then
    if [ -f "$(cat \"$VIRTUAL_ENV/$VIRTUALENVWRAPPER_PROJECT_FILENAME\")/.virtualenvwrapper/postactivate" ]; then
        source "$(cat \"$VIRTUAL_ENV/$VIRTUALENVWRAPPER_PROJECT_FILENAME\")/.virtualenvwrapper/postactivate"
    fi
fi
"""


def pre_deactivate_source(args):
    return """
if [ -f "$VIRTUAL_ENV/$VIRTUALENVWRAPPER_PROJECT_FILENAME" ]; then
    if [ -f "$(cat \"$VIRTUAL_ENV/$VIRTUALENVWRAPPER_PROJECT_FILENAME\")/.virtualenvwrapper/predeactivate" ]; then
        source "$(cat \"$VIRTUAL_ENV/$VIRTUALENVWRAPPER_PROJECT_FILENAME\")/.virtualenvwrapper/predeactivate"
    fi
fi
"""
