/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.services;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.micronaut.http.HttpMethod;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.MediaType;
import java.util.Optional;
import java.util.Set;
import javax.inject.Singleton;
import org.reactivestreams.Publisher;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

@Singleton
public class HttpRequestTraceService {

  private static final Logger LOGGER = LoggerFactory.getLogger(HttpRequestTraceService.class);

  private static final Set<String> TOP_LEVEL_SENSITIVE_FIELDS = Set.of("connectionConfiguration");

  public Publisher<Boolean> trace(final HttpRequest request) {
    return Mono.fromCallable(() -> {
      final String body = (String) request.getBody(String.class).orElse(null);

      final boolean isPrintable = request.getHeaders().getContentType().isPresent() &&
          MediaType.APPLICATION_JSON.equals(MediaType.of(request.getHeaders().getContentType().get())) &&
          isValidJson(body);

      LOGGER.info("{} {} {} {} {}", request.getRemoteAddress(), request.getMethod(), request.getUri(),
          HttpMethod.POST.equals(request.getMethod()) && body != null && isPrintable ? "- " + redactSensitiveInfo(body) : "");
      return true;
    }).subscribeOn(Schedulers.parallel()).flux();
  }

  private static String redactSensitiveInfo(final String requestBody) {
    final Optional<JsonNode> jsonNodeOpt = Jsons.tryDeserialize(requestBody);

    if (jsonNodeOpt.isPresent()) {
      final JsonNode jsonNode = jsonNodeOpt.get();
      if (jsonNode instanceof ObjectNode) {
        final ObjectNode objectNode = (ObjectNode) jsonNode;

        for (final String topLevelSensitiveField : TOP_LEVEL_SENSITIVE_FIELDS) {
          if (objectNode.has(topLevelSensitiveField)) {
            objectNode.put(topLevelSensitiveField, "REDACTED");
          }
        }

        return objectNode.toString();
      } else {
        return "Unable to deserialize POST body for logging.";
      }
    }

    return requestBody;
  }

  private static boolean isValidJson(final String json) {
    return Jsons.tryDeserialize(json).isPresent();
  }

}
