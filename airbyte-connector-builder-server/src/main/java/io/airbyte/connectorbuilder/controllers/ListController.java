/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.connectorbuilder.controllers;

import io.airbyte.connectorbuilder.ConnectorBuilderEntryPoint;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Controller("/v1/streams/list")
public class ListController {

  private static final Logger LOGGER = LoggerFactory.getLogger(ListController.class);

  private static boolean first = true;

  @Post(produces = MediaType.APPLICATION_JSON)
  public String manifest(final StreamListRequestBody body) throws IOException {
    if (first) {
      first = false;
      throw new RuntimeException("first is error");
    }
    LOGGER.info("list receive: " + ConnectorBuilderEntryPoint.toJsonString(body));
    final String response = ConnectorBuilderEntryPoint.list(body);
    if (response.charAt(0) != '{' || response.charAt(response.length() - 1) != '}') {
      throw new RuntimeException(response);
    }
    LOGGER.info("list send: " + response);
    return "{\"streams\": [{\"name\": \"messages\", \"url\": \"https://api.courier.com/messages\"}, {\"name\": \"message\", \"url\": \"https://api.courier.com/messages\"}, {\"name\": \"message_history\", \"url\": \"https://api.courier.com/messages/history\"}, {\"name\": \"message_output\", \"url\": \"https://api.courier.com/messages/output\"}]}";
  }

}
