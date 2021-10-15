/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import javax.servlet.http.HttpServletRequest;
import javax.ws.rs.container.ContainerRequestContext;
import javax.ws.rs.container.ContainerRequestFilter;
import javax.ws.rs.container.ContainerResponseContext;
import javax.ws.rs.container.ContainerResponseFilter;
import javax.ws.rs.core.Context;
import org.apache.commons.io.IOUtils;
import org.eclipse.jetty.http.HttpStatus;
import org.glassfish.jersey.message.MessageUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class RequestLogger implements ContainerRequestFilter, ContainerResponseFilter {

  private static final Logger LOGGER = LoggerFactory.getLogger(RequestLogger.class);

  @Context
  private HttpServletRequest servletRequest;

  private String requestBody = null;

  private final Map<String, String> mdc;

  public RequestLogger(Map<String, String> mdc) {
    this.mdc = mdc;
  }

  @VisibleForTesting
  RequestLogger(Map<String, String> mdc, HttpServletRequest servletRequest) {
    this.mdc = mdc;
    this.servletRequest = servletRequest;
  }

  @Override
  public void filter(ContainerRequestContext requestContext) throws IOException {
    if (requestContext.getMethod().equals("POST")) {
      // hack to refill the entity stream so it doesn't interfere with other operations
      ByteArrayOutputStream baos = new ByteArrayOutputStream();
      IOUtils.copy(requestContext.getEntityStream(), baos);
      InputStream entity = new ByteArrayInputStream(baos.toByteArray());
      requestContext.setEntityStream(new ByteArrayInputStream(baos.toByteArray()));
      // end hack

      requestBody = IOUtils.toString(entity, MessageUtils.getCharset(requestContext.getMediaType()));
    }
  }

  @Override
  public void filter(ContainerRequestContext requestContext, ContainerResponseContext responseContext) {
    MDC.setContextMap(mdc);

    String remoteAddr = servletRequest.getRemoteAddr();
    String method = servletRequest.getMethod();
    String url = servletRequest.getRequestURI();

    boolean isPrintable = servletRequest.getHeader("Content-Type") != null &&
        servletRequest.getHeader("Content-Type").toLowerCase().contains("application/json") &&
        isValidJson(requestBody);

    int status = responseContext.getStatus();

    StringBuilder logBuilder = createLogPrefix(
        remoteAddr,
        method,
        status,
        url);

    if (method.equals("POST") && requestBody != null && !requestBody.equals("") && isPrintable) {
      logBuilder
          .append(" - ")
          .append(redactSensitiveInfo(requestBody));
    }

    if (HttpStatus.isClientError(status) || HttpStatus.isServerError(status)) {
      LOGGER.error(logBuilder.toString());
    } else {
      LOGGER.info(logBuilder.toString());
    }
  }

  @VisibleForTesting
  static StringBuilder createLogPrefix(
                                       String remoteAddr,
                                       String method,
                                       int status,
                                       String url) {
    return new StringBuilder()
        .append("REQ ")
        .append(remoteAddr)
        .append(" ")
        .append(method)
        .append(" ")
        .append(status)
        .append(" ")
        .append(url);
  }

  private static final Set<String> TOP_LEVEL_SENSITIVE_FIELDS = Set.of(
      "connectionConfiguration");

  private static String redactSensitiveInfo(String requestBody) {
    Optional<JsonNode> jsonNodeOpt = Jsons.tryDeserialize(requestBody);

    if (jsonNodeOpt.isPresent()) {
      JsonNode jsonNode = jsonNodeOpt.get();
      if (jsonNode instanceof ObjectNode) {
        ObjectNode objectNode = (ObjectNode) jsonNode;

        for (String topLevelSensitiveField : TOP_LEVEL_SENSITIVE_FIELDS) {
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

  private static boolean isValidJson(String json) {
    return Jsons.tryDeserialize(json).isPresent();
  }

}
