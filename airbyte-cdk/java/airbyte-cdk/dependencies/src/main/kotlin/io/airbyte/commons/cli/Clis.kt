/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.cli

import org.apache.commons.cli.*

object Clis {
    /**
     * Parse an options object
     *
     * @param args
     * - command line args
     * @param options
     * - expected options
     * @return object with parsed values.
     */
    @JvmOverloads
    fun parse(
        args: Array<String>,
        options: Options,
        parser: CommandLineParser = DefaultParser(),
        commandLineSyntax: String? = null
    ): CommandLine {
        val helpFormatter = HelpFormatter()

        try {
            return parser.parse(options, args)
        } catch (e: ParseException) {
            if (!commandLineSyntax.isNullOrEmpty()) {
                helpFormatter.printHelp(commandLineSyntax, options)
            }
            throw IllegalArgumentException(e)
        }
    }

    fun parse(args: Array<String>, options: Options, commandLineSyntax: String?): CommandLine {
        return parse(args, options, DefaultParser(), commandLineSyntax)
    }

    fun getRelaxedParser(): CommandLineParser = RelaxedParser()

    // https://stackoverflow.com/questions/33874902/apache-commons-cli-1-3-1-how-to-ignore-unknown-arguments
    private class RelaxedParser : DefaultParser() {
        @Throws(ParseException::class)
        override fun parse(options: Options, arguments: Array<String>): CommandLine {
            val knownArgs: MutableList<String> = ArrayList()
            for (i in arguments.indices) {
                if (options.hasOption(arguments[i])) {
                    knownArgs.add(arguments[i])
                    if (i + 1 < arguments.size && options.getOption(arguments[i]).hasArg()) {
                        knownArgs.add(arguments[i + 1])
                    }
                }
            }
            return super.parse(options, knownArgs.toTypedArray<String>())
        }
    }
}
