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
import org.reactivestreams.Publisher;

@Filter("/**")
public class BodySetterFilter implements HttpServerFilter {

  @Override
  public Publisher<MutableHttpResponse<?>> doFilter(final HttpRequest<?> request, final ServerFilterChain chain) {

    if (request.getMethod() == HttpMethod.POST) {

      // hack to refill the entity stream so it doesn't interfere with other operations
      /*
       * final ByteArrayOutputStream baos = new ByteArrayOutputStream();
       * IOUtils.copy(request.getAttribute(), baos); final InputStream entity = new
       * ByteArrayInputStream(baos.toByteArray()); requestContext.setEntityStream(new
       * ByteArrayInputStream(baos.toByteArray()));
       */
      // end hack
    }

    return chain.proceed(request);
  }

}
