/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.filters;

import com.google.common.net.HttpHeaders;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.MutableHttpResponse;
import io.micronaut.http.annotation.Filter;
import io.micronaut.http.filter.HttpServerFilter;
import io.micronaut.http.filter.ServerFilterChain;
import java.util.Map;
import org.reactivestreams.Publisher;

// https://medium.com/@Leejjon_net/how-to-allow-cross-origin-requests-in-a-jax-rs-microservice-d2a6aa2df484
@Filter("/**")
public class CorsFilter implements HttpServerFilter {

  public static final Map<String, String> MAP = Map.of(
      HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN, "*",
      HttpHeaders.ACCESS_CONTROL_ALLOW_HEADERS, "Origin, Content-Type, Accept, Content-Encoding",
      HttpHeaders.ACCESS_CONTROL_ALLOW_METHODS, "GET, POST, PUT, DELETE, OPTIONS, HEAD");

  @Override
  public Publisher<MutableHttpResponse<?>> doFilter(final HttpRequest<?> request, final ServerFilterChain chain) {
    for (final Map.Entry<String, String> entry : MAP.entrySet()) {
      request.setAttribute(entry.getKey(), entry.getValue());
    }

    return chain.proceed(request);
  }

}
