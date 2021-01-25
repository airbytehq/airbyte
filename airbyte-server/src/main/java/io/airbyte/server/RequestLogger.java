/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
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
    int status = responseContext.getStatus();

    StringBuilder logBuilder = new StringBuilder()
        .append("REQ ")
        .append(remoteAddr)
        .append(" ")
        .append(method)
        .append(" ")
        .append(status)
        .append(" ")
        .append(url);

    if (method.equals("POST") && requestBody != null && !requestBody.equals("")) {
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

}
