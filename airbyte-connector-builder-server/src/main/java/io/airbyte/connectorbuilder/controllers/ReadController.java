package io.airbyte.connectorbuilder.controllers;

import io.airbyte.connectorbuilder.ConnectorBuilderEntryPoint;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;

@Controller("/v1/stream/read")
public class ReadController {
    private static final Logger LOGGER = LoggerFactory.getLogger(ReadController.class);

    @Post(produces = MediaType.APPLICATION_JSON)
    public String manifest(final StreamReadRequestBody body) throws IOException, InterruptedException {
        LOGGER.info("read receive: " + ConnectorBuilderEntryPoint.toJsonString(body));
        final String response = ConnectorBuilderEntryPoint.read(body);
        LOGGER.info("read send: " + response);
        return response;
    }
}
