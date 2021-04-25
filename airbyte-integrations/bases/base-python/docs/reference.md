Usage: pydoc-markdown [OPTIONS] [CONFIG]

  Pydoc-Markdown is a renderer for Python API documentation in Markdown
  format.

  With no arguments it will load the default configuration file. If the
  *config* argument is specified, it must be the name of a configuration
  file or a YAML formatted object for the configuration.

Options:
  --version                       Show the version and exit.
  --bootstrap [base|mkdocs|hugo|readthedocs|docusaurus]
                                  Create a Pydoc-Markdown configuration file
                                  in the current working directory.

  -v, --verbose                   Increase log verbosity.
  -q, --quiet                     Decrease the log verbosity.
  -m, --module MODULE             The module to parse and generated API
                                  documentation for. Can be specified multiple
                                  times. Using this option will disable
                                  loading the default configuration file.

  -p, --package PACKAGE           The package to parse and generated API
                                  documentation for including all sub-packages
                                  and -modules. Can be specified multiple
                                  times. Using this option will disable
                                  loading the default configuration file.

  -I, --search-path PATH          A directory to use in the search for Python
                                  modules. Can be specified multiple times.
                                  Using this option will disable loading the
                                  default configuration file.

  --py2 / --py3                   Switch between parsing Python 2 and Python 3
                                  code. The default is Python 3. Using --py2
                                  will enable parsing code that uses the
                                  "print" statement. This is equivalent of
                                  setting the print_function option of the
                                  "python" loader to False. Using this option
                                  will disable loading the default
                                  configuration file.

  --render-toc / --no-render-toc  Enable/disable the rendering of the TOC in
                                  the "markdown" renderer.

  -s, --server                    Watch for file changes and re-render if
                                  needed and start the server for the
                                  configured renderer. This doesn't work for
                                  all renderers.

  -o, --open                      Open the browser after starting the server
                                  with -s,--server.

  --dump                          Dump the loaded modules in Docspec JSON
                                  format to stdout, after the processors.

  --with-processors / --without-processors
                                  Enable/disable processors. Only with --dump.
  --build                         Invoke a build after the Markdown files are
                                  produced. Note that some renderers may not
                                  support this option (e.g. the "markdown"
                                  renderer).

  --site-dir TEXT                 Set the output directory when using --build.
  --help                          Show this message and exit.
