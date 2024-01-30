package io.airbyte.cdk.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.base.consumers.WriteStreamConsumer;
import io.airbyte.cdk.integrations.base.util.ShutdownUtils;
import io.airbyte.cdk.integrations.util.ApmTraceUtils;
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.micronaut.context.env.Environment;
import io.micronaut.core.util.StringUtils;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import picocli.CommandLine;

import java.nio.file.Path;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
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

    @Inject
    private Integration integration;

    @Inject
    @Named("outputRecordCollector")
    private Consumer<AirbyteMessage> outputRecordCollector;

    @Inject
    private JsonSchemaValidator validator;

    @Inject
    private Environment environment;

    @Inject
    private ShutdownUtils shutdownUtils;

    @Inject
    private WriteStreamConsumer writeStreamConsumer;

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
            "Required by the following commands: check, discover, read, write",
            JavaBaseConstants.ARGS_CONFIG_DESC
    })
    private String config;

    @CommandLine.Option(names = {  "--" + JavaBaseConstants.ARGS_CATALOG_KEY }, description = {
            "Required by the following commands: read, write",
            JavaBaseConstants.ARGS_CATALOG_DESC
    })
    private String catalog;

    @CommandLine.Option(names = {  "--" + JavaBaseConstants.ARGS_STATE_KEY }, description = {
            "Required by the following commands: read",
            JavaBaseConstants.ARGS_PATH_DESC
    })
    private Optional<String> state;

    @Override
    public void run() {
        try {
            switch (Command.valueOf(command.toUpperCase(Locale.ROOT))) {
                case SPEC:
                    LOGGER.info("Spec command");
                    spec();
                    break;
                case CHECK:
                    LOGGER.info("Check command");
                    check();
                    break;
                case DISCOVER:
                    LOGGER.info("Discover command");
                    discover();
                    break;
                case READ:
                    LOGGER.info("Read command");
                    read();
                    break;
                case WRITE:
                    LOGGER.info("Write command");
                    write();
                    break;
                default:
                    throw new IllegalArgumentException("Unexpected value: " + command);
            }
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

        LOGGER.info("Completed integration: {}", this.integration.getClass().getName());
    }

    private JsonNode validateConfig(JsonNode schemaJson, String config, String operationType) throws Exception {
        if(StringUtils.isNotEmpty(config)) {
            final JsonNode configJson = Jsons.deserialize(IOs.readFile(Path.of(catalog)));
            final Set<String> validationResult = validator.validate(schemaJson, configJson);
            if (!validationResult.isEmpty()) {
                throw new Exception(String.format("Verification error(s) occurred for %s. Errors: %s ", operationType, validationResult));
            }
            return configJson;
        } else {
            throw new IllegalArgumentException("Missing required command line argument '--" + JavaBaseConstants.ARGS_CONFIG_KEY + "'.");
        }
    }

    private ConfiguredAirbyteCatalog validateCatalog(final String catalog) {
        if(StringUtils.isNotEmpty(catalog)) {
            return Jsons.deserialize(IOs.readFile(Path.of(catalog)), ConfiguredAirbyteCatalog.class);
        } else {
            throw new IllegalArgumentException("Missing required command line argument '--" + JavaBaseConstants.ARGS_CATALOG_KEY + "'.");
        }
    }

    private void initialize(final JsonNode config) {
        if(environment.getActiveNames().contains("destination")) {
            DestinationConfig.initialize(config, ((Destination) integration).isV2Destination());
        }
    }

    private void check() {
        try {
            final JsonNode configJson = validateConfig(this.integration.spec().getConnectionSpecification(), config, Command.CHECK.name());
            initialize(configJson);
            this.outputRecordCollector.accept((new AirbyteMessage()).withType(AirbyteMessage.Type.CONNECTION_STATUS).withConnectionStatus(this.integration.check(configJson)));
        } catch (final Exception e) {
            this.outputRecordCollector.accept((new AirbyteMessage()).withType(AirbyteMessage.Type.CONNECTION_STATUS).withConnectionStatus((new AirbyteConnectionStatus()).withStatus(AirbyteConnectionStatus.Status.FAILED).withMessage(e.getMessage())));
        }
    }

    private void discover() throws Exception {
        final JsonNode configJson = validateConfig(this.integration.spec().getConnectionSpecification(), config, Command.DISCOVER.name());
        this.outputRecordCollector.accept((new AirbyteMessage()).withType(AirbyteMessage.Type.CATALOG).withCatalog(((Source)integration).discover(configJson)));
    }

    private void read() throws Exception {
        final JsonNode configJson = validateConfig(integration.spec().getConnectionSpecification(), config, Command.READ.name());
        final ConfiguredAirbyteCatalog configuredCatalog = validateCatalog(catalog);
        final Optional<JsonNode> stateOptional = state.isPresent() ? state.map(s -> Path.of(s)).map(f -> Jsons.deserialize(IOs.readFile(f))) : Optional.empty();
        AutoCloseableIterator<AirbyteMessage> messageIterator = null;
        try {
            // TODO make the message iterator injectable
            messageIterator = ((Source)integration).read(configJson, configuredCatalog, stateOptional.orElse(null));
            messageIterator.getAirbyteStream().ifPresent(s -> LOGGER.debug("Producing messages for stream {}...", s));
            messageIterator.forEachRemaining(outputRecordCollector);
            messageIterator.getAirbyteStream().ifPresent(s -> LOGGER.debug("Finished producing messages for stream {}..."));
        } finally {
            if (messageIterator != null) {
                messageIterator.close();
            }
            if (integration instanceof AutoCloseable) {
                ((AutoCloseable) integration).close();
            }
            shutdownUtils.stopOrphanedThreads(ShutdownUtils.EXIT_HOOK,
                    ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
                    TimeUnit.MINUTES,
                    ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
                    TimeUnit.MINUTES);
        }
    }

    private void spec() throws Exception {
        this.outputRecordCollector.accept((new AirbyteMessage()).withType(AirbyteMessage.Type.SPEC).withSpec(this.integration.spec()));
    }

    private void write() throws Exception {
        final JsonNode configJson = validateConfig(integration.spec().getConnectionSpecification(), config, Command.WRITE.name());
        // save config to singleton
        initialize(configJson);
        final ConfiguredAirbyteCatalog configuredCatalog = validateCatalog(catalog);

        SerializedAirbyteMessageConsumer consumer = null;
        try {
            // TODO make the message consumer injectable
            consumer = ((Destination)integration).getSerializedMessageConsumer(configJson, configuredCatalog, outputRecordCollector);
            writeStreamConsumer.consumeWriteStream(consumer);
        } finally {
            if (consumer != null) {
                consumer.close();
            }
            shutdownUtils.stopOrphanedThreads(ShutdownUtils.EXIT_HOOK,
                    ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
                    TimeUnit.MINUTES,
                    ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
                    TimeUnit.MINUTES);
        }
    }
}
