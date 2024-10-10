# encoding: utf-8
#
# Copyright (c) 2010 Doug Hellmann.  All rights reserved.
#
"""Load hooks for virtualenvwrapper.
"""

import inspect
import itertools
import logging
import logging.handlers
import optparse
import os
import sys

from stevedore import ExtensionManager, NamedExtensionManager

import virtualenvwrapper.version

LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'


class GroupWriteRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Taken from http://stackoverflow.com/questions/1407474
    """
    def _open(self):
        prevumask = os.umask(0o002)
        rtv = logging.handlers.RotatingFileHandler._open(self)
        os.umask(prevumask)
        return rtv


def main():
    parser = optparse.OptionParser(
        usage='usage: %prog [options] <hook> [<arguments>]',
        prog='virtualenvwrapper.hook_loader',
        description='Manage hooks for virtualenvwrapper',
    )

    parser.add_option(
        '-S', '--script',
        help='Runs "hook" then "<hook>_source", writing the ' +
        'result to <file>',
        dest='script_filename',
        default=None,
    )
    parser.add_option(
        '-s', '--source',
        help='Print the shell commands to be run in the current shell',
        action='store_true',
        dest='sourcing',
        default=False,
    )
    parser.add_option(
        '-l', '--list',
        help='Print a list of the plugins available for the given hook',
        action='store_true',
        default=False,
        dest='listing',
    )
    parser.add_option(
        '-v', '--verbose',
        help='Show more information on the console',
        action='store_const',
        const=2,
        default=1,
        dest='verbose_level',
    )
    parser.add_option(
        '-q', '--quiet',
        help='Show less information on the console',
        action='store_const',
        const=0,
        dest='verbose_level',
    )
    parser.add_option(
        '-n', '--name',
        help='Only run the hook from the named plugin',
        action='append',
        dest='names',
        default=[],
    )
    parser.add_option(
        '--version',
        help='Show the version of virtualenvwrapper',
        action='store_true',
        default=False,
    )
    parser.disable_interspersed_args()  # stop when on option without an '-'
    options, args = parser.parse_args()

    if options.version:
        print(virtualenvwrapper.version.version)
        return 0

    root_logger = logging.getLogger('virtualenvwrapper')

    # Set up logging to a file
    logfile = os.environ.get('VIRTUALENVWRAPPER_LOG_FILE')
    if logfile:
        root_logger.setLevel(logging.DEBUG)
        file_handler = GroupWriteRotatingFileHandler(
            logfile,
            maxBytes=10240,
            backupCount=1,
        )
        formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Send higher-level messages to the console, too
    console = logging.StreamHandler(sys.stderr)
    console_level = [logging.WARNING,
                     logging.INFO,
                     logging.DEBUG,
                     ][options.verbose_level]
    console.setLevel(console_level)
    formatter = logging.Formatter('%(name)s %(message)s')
    console.setFormatter(formatter)
    root_logger.addHandler(console)
    root_logger.setLevel(console_level)

    # logging.getLogger(__name__).debug('cli args %s', args)

    # Determine which hook we're running
    if not args:
        if options.listing:
            list_hooks()
            return 0
        else:
            parser.error('Please specify the hook to run')
    hook = args[0]

    if options.sourcing and options.script_filename:
        parser.error('--source and --script are mutually exclusive.')

    if options.sourcing:
        hook += '_source'

    log = logging.getLogger('virtualenvwrapper.hook_loader')

    log.debug('Running %s hooks', hook)
    run_hooks(hook, options, args)

    if options.script_filename:
        log.debug('Saving sourcable %s hooks to %s',
                  hook, options.script_filename)
        options.sourcing = True
        try:
            with open(options.script_filename, "w") as output:
                output.write('# %s\n' % hook)
                # output.write('echo %s\n' % hook)
                # output.write('set -x\n')
                run_hooks(hook + '_source', options, args, output)
        except (IOError, OSError) as e:
            log.error('Error while writing to %s: \n %s',
                      options.script_filename, e)
            sys.exit(1)

    return 0


def run_hooks(hook, options, args, output=None):
    log = logging.getLogger('virtualenvwrapper.hook_loader')
    if output is None:
        output = sys.stdout

    namespace = 'virtualenvwrapper.%s' % hook
    if options.names:
        log.debug('looking for %s hooks %s' % (namespace, options.names))
        hook_mgr = NamedExtensionManager(namespace, options.names)
    else:
        log.debug('looking for %s hooks' % namespace)
        hook_mgr = ExtensionManager(namespace)

    if options.listing:
        def show(ext):
            output.write('  %-10s -- %s\n' %
                         (ext.name, inspect.getdoc(ext.plugin) or ''))
        try:
            hook_mgr.map(show)
        except RuntimeError:  # no templates
            output.write('  No templates installed.\n')

    elif options.sourcing:
        def get_source(ext, args):
            # Show the shell commands so they can
            # be run in the calling shell.
            log.debug('getting source instructions for %s' % ext.name)
            contents = (ext.plugin(args) or '').strip()
            if contents:
                output.write('# %s\n' % ext.name)
                output.write(contents)
                output.write("\n")
        try:
            hook_mgr.map(get_source, args[1:])
        except RuntimeError:
            pass

    else:
        # Just run the plugin ourselves
        def invoke(ext, args):
            log.debug('running %s' % ext.name)
            ext.plugin(args)
        try:
            hook_mgr.map(invoke, args[1:])
        except RuntimeError:
            pass


def list_hooks(output=None):
    if output is None:
        output = sys.stdout
    static_names = [
        'initialize',
        'get_env_details',
        'project.pre_mkproject',
        'project.post_mkproject',
        'project.template',
    ]
    pre_post_hooks = (
        '_'.join(h)
        for h in itertools.product(['pre', 'post'],
                                   ['mkvirtualenv',
                                    'rmvirtualenv',
                                    'activate',
                                    'deactivate',
                                    'cpvirtualenv',
                                    ])
    )
    for hook in itertools.chain(static_names, pre_post_hooks):
        output.write(hook + '\n')


if __name__ == '__main__':
    main()
