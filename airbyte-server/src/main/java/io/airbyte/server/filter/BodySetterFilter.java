/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.filter;

import io.micronaut.http.HttpMethod;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.MutableHttpResponse;
import io.micronaut.http.annotation.Filter;
import io.micronaut.http.filter.HttpServerFilter;
import io.micronaut.http.filter.ServerFilterChain;
import java.nio.ByteBuffer;
import lombok.extern.slf4j.Slf4j;
import org.reactivestreams.Publisher;

@Filter("/**")
@Slf4j
public class BodySetterFilter implements HttpServerFilter {

  @Override
  public Publisher<MutableHttpResponse<?>> doFilter(final HttpRequest<?> request, final ServerFilterChain chain) {

    if (request.getMethod() == HttpMethod.POST) {

      request.getAttributes().forEach(
          (k, v) -> {
            log.error(k);
            log.error(v.toString());
          });

      log.error("Content length: " + request.getContentLength());

      log.error("Request type: " + request.getClass().getName());
      log.error("Request type cano: " + request.getClass().getCanonicalName());

      request.getParameters().forEach(
          (k, v) -> {
            log.error(k);
            log.error(v.toString());
          });

      if (request.getBody(ByteBuffer.class).isEmpty()) {
        log.error("Empty body");
      } else {
        log.error(request.getBody(ByteBuffer.class).get().toString());
      }

      // log.error(request.getBody().get().toString());

      // hack to refill the entity stream so it doesn't interfere with other operations

      // final ByteArrayOutputStream baos = new ByteArrayOutputStream();
      // IOUtils.copy(request.getAttribute(), baos);
      // final InputStream entity = new ByteArrayInputStream(baos.toByteArray());
      // requestContext.setEntityStream(new
      // ByteArrayInputStream(baos.toByteArray()));

      // end hack
    }

    return chain.proceed(request);
  }

}
