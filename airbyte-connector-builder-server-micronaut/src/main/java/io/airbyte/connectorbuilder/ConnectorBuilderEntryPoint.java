/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.connectorbuilder;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.connectorbuilder.controllers.StreamListRequestBody;
import io.airbyte.connectorbuilder.controllers.StreamReadRequestBody;
import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;
import org.apache.commons.io.IOUtils;

public class ConnectorBuilderEntryPoint {

  public static String read(final StreamReadRequestBody body) throws IOException {
    return runEntrypoint("read", toJsonString(body));
  }

  public static String list(final StreamListRequestBody body) throws IOException {
    return runEntrypoint("list", toJsonString(body));
  }

  private static String runEntrypoint(final String command, final String argumentAsJsonString) throws IOException {
    final ProcessBuilder processBuilder = new ProcessBuilder("python3.9", "connector_builder/entrypoint.py", command, argumentAsJsonString);
    processBuilder.redirectErrorStream(true);

    final Process process = processBuilder.start();

    final List<String> results = IOUtils.readLines(process.getInputStream());

    // hack: Return last message...
    if (results.isEmpty()) {
      throw new RuntimeException("No results...");
    } else {

      return (results.stream()
          .filter(s -> !s.contains("LOG"))
          .filter(s -> !s.contains("DEBUG"))
          .collect(Collectors.joining())
          .replace("'", "\""));
    }
  }

  public static <T> String toJsonString(final T object) throws JsonProcessingException {
    return new ObjectMapper().writer().writeValueAsString(object);
  }

  public static <T> T fromJsonString(final String s, final Class<T> c) throws JsonProcessingException {
    return new ObjectMapper().readValue(s, c);
  }

}
