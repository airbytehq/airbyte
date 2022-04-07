/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.filters;

import io.airbyte.server.services.HttpRequestTraceService;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.MutableHttpResponse;
import io.micronaut.http.annotation.Filter;
import io.micronaut.http.filter.HttpServerFilter;
import io.micronaut.http.filter.ServerFilterChain;
import javax.inject.Inject;
import org.reactivestreams.Publisher;
import reactor.core.publisher.Flux;

@Filter("/**")
public class RequestLoggerFilter implements HttpServerFilter {

  @Inject
  private HttpRequestTraceService httpRequestTraceService;

  @Override
  public Publisher<MutableHttpResponse<?>> doFilter(final HttpRequest<?> request, final ServerFilterChain chain) {
    return Flux.from(httpRequestTraceService.trace(request)).switchMap(b -> chain.proceed(request));
  }

}
