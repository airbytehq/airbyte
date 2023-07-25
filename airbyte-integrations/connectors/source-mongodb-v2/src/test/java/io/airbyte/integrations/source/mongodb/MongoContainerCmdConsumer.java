package io.airbyte.integrations.source.mongodb;

import com.github.dockerjava.api.command.CreateContainerCmd;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.function.Consumer;

public record MongoContainerCmdConsumer(String name) implements Consumer<CreateContainerCmd> {

    private static final Logger LOGGER = LoggerFactory.getLogger(MongoContainerCmdConsumer.class);

    @Override
    public void accept(final CreateContainerCmd createContainerCmd) {
        LOGGER.info("Setting name and hostname to {}...", name);
        createContainerCmd.withName(name).withHostName(name);
    }

}
