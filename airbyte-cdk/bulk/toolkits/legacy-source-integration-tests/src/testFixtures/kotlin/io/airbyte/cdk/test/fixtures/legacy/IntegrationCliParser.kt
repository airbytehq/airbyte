package io.airbyte.cdk.test.fixtures.legacy

import com.google.common.base.Preconditions
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.commons.cli.Option
import org.apache.commons.cli.OptionGroup
import org.apache.commons.cli.Options
import java.nio.file.Path
import java.util.*

private val LOGGER = KotlinLogging.logger {}
/** Parses command line args to a type safe config object for each command type. */
class IntegrationCliParser {
    fun parse(args: Array<String>): IntegrationConfig {
        val command = parseCommand(args)
        return parseOptions(args, command)
    }

    companion object {

        private val COMMAND_GROUP: OptionGroup

        init {
            val optionGroup = OptionGroup()
            optionGroup.isRequired = true

            optionGroup.addOption(
                Option.builder()
                    .longOpt(Command.SPEC.toString().lowercase(Locale.getDefault()))
                    .desc("outputs the json configuration specification")
                    .build()
            )
            optionGroup.addOption(
                Option.builder()
                    .longOpt(Command.CHECK.toString().lowercase(Locale.getDefault()))
                    .desc("checks the config can be used to connect")
                    .build()
            )
            optionGroup.addOption(
                Option.builder()
                    .longOpt(Command.DISCOVER.toString().lowercase(Locale.getDefault()))
                    .desc("outputs a catalog describing the source's catalog")
                    .build()
            )
            optionGroup.addOption(
                Option.builder()
                    .longOpt(Command.READ.toString().lowercase(Locale.getDefault()))
                    .desc("reads the source and outputs messages to STDOUT")
                    .build()
            )
            optionGroup.addOption(
                Option.builder()
                    .longOpt(Command.WRITE.toString().lowercase(Locale.getDefault()))
                    .desc("writes messages from STDIN to the integration")
                    .build()
            )

            COMMAND_GROUP = optionGroup
        }

        private fun parseCommand(args: Array<String>): Command {
            val options = Options()
            options.addOptionGroup(COMMAND_GROUP)

            val parsed = Clis.parse(args, options, Clis.getRelaxedParser())
            return Command.valueOf(parsed.options[0].longOpt.uppercase(Locale.getDefault()))
        }

        private fun parseOptions(args: Array<String>, command: Command): IntegrationConfig {
            val options = Options()
            options.addOptionGroup(
                COMMAND_GROUP
            ) // so that the parser does not throw an exception when encounter command args.

            when (command) {
                Command.SPEC -> {
                    // no args.
                }
                Command.CHECK,
                Command.DISCOVER ->
                    options.addOption(
                        Option.builder()
                            .longOpt(JavaBaseConstants.ARGS_CONFIG_KEY)
                            .desc(JavaBaseConstants.ARGS_CONFIG_DESC)
                            .hasArg(true)
                            .required(true)
                            .build()
                    )
                Command.READ -> {
                    options.addOption(
                        Option.builder()
                            .longOpt(JavaBaseConstants.ARGS_CONFIG_KEY)
                            .desc(JavaBaseConstants.ARGS_CONFIG_DESC)
                            .hasArg(true)
                            .required(true)
                            .build()
                    )
                    options.addOption(
                        Option.builder()
                            .longOpt(JavaBaseConstants.ARGS_CATALOG_KEY)
                            .desc(JavaBaseConstants.ARGS_CATALOG_DESC)
                            .hasArg(true)
                            .build()
                    )
                    options.addOption(
                        Option.builder()
                            .longOpt(JavaBaseConstants.ARGS_STATE_KEY)
                            .desc(JavaBaseConstants.ARGS_PATH_DESC)
                            .hasArg(true)
                            .build()
                    )
                }
                Command.WRITE -> {
                    options.addOption(
                        Option.builder()
                            .longOpt(JavaBaseConstants.ARGS_CONFIG_KEY)
                            .desc(JavaBaseConstants.ARGS_CONFIG_DESC)
                            .hasArg(true)
                            .required(true)
                            .build()
                    )
                    options.addOption(
                        Option.builder()
                            .longOpt(JavaBaseConstants.ARGS_CATALOG_KEY)
                            .desc(JavaBaseConstants.ARGS_CATALOG_DESC)
                            .hasArg(true)
                            .build()
                    )
                }
            }
            val parsed =
                Clis.parse(args, options, command.toString().lowercase(Locale.getDefault()))
            Preconditions.checkNotNull(parsed)
            val argsMap: MutableMap<String?, String?> = HashMap()
            for (option in parsed.options) {
                argsMap[option.longOpt] = option.value
            }
            LOGGER.info { "integration args: $argsMap" }

            return when (command) {
                Command.SPEC -> {
                    IntegrationConfig.Companion.spec()
                }
                Command.CHECK -> {
                    IntegrationConfig.Companion.check(
                        Path.of(argsMap[JavaBaseConstants.ARGS_CONFIG_KEY])
                    )
                }
                Command.DISCOVER -> {
                    IntegrationConfig.Companion.discover(
                        Path.of(argsMap[JavaBaseConstants.ARGS_CONFIG_KEY])
                    )
                }
                Command.READ -> {
                    IntegrationConfig.Companion.read(
                        Path.of(argsMap[JavaBaseConstants.ARGS_CONFIG_KEY]),
                        Path.of(argsMap[JavaBaseConstants.ARGS_CATALOG_KEY]),
                        if (argsMap.containsKey(JavaBaseConstants.ARGS_STATE_KEY))
                            Path.of(argsMap[JavaBaseConstants.ARGS_STATE_KEY])
                        else null
                    )
                }
                Command.WRITE -> {
                    IntegrationConfig.Companion.write(
                        Path.of(argsMap[JavaBaseConstants.ARGS_CONFIG_KEY]),
                        Path.of(argsMap[JavaBaseConstants.ARGS_CATALOG_KEY])
                    )
                }
            }
        }
    }
}
