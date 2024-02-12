package io.airbyte.cdk.integrations.base;

import io.airbyte.cdk.integrations.base.operation.Operation;
import io.airbyte.cdk.integrations.base.operation.OperationType;
import io.airbyte.cdk.integrations.base.util.ShutdownUtils;
import io.airbyte.cdk.integrations.util.ApmTraceUtils;
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.micronaut.context.annotation.Value;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import picocli.CommandLine;

import java.nio.file.Path;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

@CommandLine.Command(name = "", description = "", mixinStandardHelpOptions = true,
    header = {
        "@|magenta     ___    _      __          __       |@",
        "@|magenta    /   |  (_)____/ /_  __  __/ /____   |@",
        "@|magenta   / /| | / / ___/ __ \\/ / / / __/ _   |@",
        "@|magenta  / ___ |/ / /  / /_/ / /_/ / /_/  __/  |@",
        "@|magenta /_/  |_/_/_/  /_.___/\\__, /\\__/\\___/|@",
        "@|magenta                    /____/              |@"
    })
public class IntegrationCommand implements Runnable {

    private static final Logger LOGGER = LoggerFactory.getLogger(IntegrationCommand.class);

    @Value("${micronaut.application.name}")
    private String connectorName;

    @Inject
    private List<Operation> operations;

    @Inject
    @Named("outputRecordCollector")
    private  Consumer<AirbyteMessage> outputRecordCollector;

    @CommandLine.Parameters(index = "0", description = {
            "The command to execute (check|discover|read|spec|write)",
            "\t check - checks the config can be used to connect",
            "\t discover - outputs a catalog describing the source's catalog",
            "\t read - reads the source and outputs messages to STDOUT",
            "\t spec - outputs the json configuration specification",
            "\t write - writes messages from STDIN to the integration"
    })
    private String command;

    @CommandLine.Option(names = { "--" + JavaBaseConstants.ARGS_CONFIG_KEY }, description = {
            JavaBaseConstants.ARGS_CONFIG_DESC,
            "Required by the following commands: check, discover, read, write"
    })
    private Path configFile;

    @CommandLine.Option(names = {  "--" + JavaBaseConstants.ARGS_CATALOG_KEY }, description = {
            JavaBaseConstants.ARGS_CATALOG_DESC,
            "Required by the following commands: read, write"
    })
    private Path catalogFile;

    @CommandLine.Option(names = {  "--" + JavaBaseConstants.ARGS_STATE_KEY }, description = {
            JavaBaseConstants.ARGS_PATH_DESC,
            "Required by the following commands: read",
    })
    private Optional<Path> stateFile;

    @Override
    public void run() {
        try {
            execute(OperationType.valueOf(command.toUpperCase(Locale.ROOT)));
        } catch (final Exception e) {
            LOGGER.error("Unable to perform operation {}.", command, e);
            // Many of the exceptions thrown are nested inside layers of RuntimeExceptions. An attempt is made
            // to
            // find the root exception that corresponds to a configuration error. If that does not exist, we
            // just return the original exception.
            ApmTraceUtils.addExceptionToTrace(e);
            final Throwable rootThrowable = ConnectorExceptionUtil.getRootConfigError(e);
            final String displayMessage = ConnectorExceptionUtil.getDisplayMessage(rootThrowable);
            // If the source connector throws a config error, a trace message with the relevant message should
            // be surfaced.
            if (ConnectorExceptionUtil.isConfigError(rootThrowable)) {
                AirbyteTraceMessageUtility.emitConfigErrorTrace(e, displayMessage);
            }
            if (Command.valueOf(command.toUpperCase(Locale.ROOT)).equals(Command.CHECK)) {
                // Currently, special handling is required for the CHECK case since the user display information in
                // the trace message is
                // not properly surfaced to the FE. In the future, we can remove this and just throw an exception.
                outputRecordCollector
                        .accept(
                                new AirbyteMessage()
                                        .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                                        .withConnectionStatus(
                                                new AirbyteConnectionStatus()
                                                        .withStatus(AirbyteConnectionStatus.Status.FAILED)
                                                        .withMessage(displayMessage)));
                return;
            }
        }

        LOGGER.info("Completed integration: {}", connectorName);
    }

    private void execute(final OperationType operationType) throws Exception {
        final Optional<Operation> operation = operations.stream().filter(o -> operationType.equals(o.type())).findFirst();
        if(operation.isPresent()) {
            operation.get().execute();
        } else {
            throw new IllegalArgumentException("Connector does not support the '" +
                    operationType.name().toLowerCase(Locale.ROOT) + "' operation.");
        }
    }
}
