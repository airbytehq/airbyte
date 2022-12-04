/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import com.google.common.collect.ImmutableMap;
import com.google.common.net.HttpHeaders;
import java.util.Map;
import javax.ws.rs.container.ContainerRequestContext;
import javax.ws.rs.container.ContainerResponseContext;
import javax.ws.rs.container.ContainerResponseFilter;

// https://medium.com/@Leejjon_net/how-to-allow-cross-origin-requests-in-a-jax-rs-microservice-d2a6aa2df484
public class CorsFilter implements ContainerResponseFilter {

  public static final ImmutableMap<String, String> MAP = ImmutableMap.of(
      HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN, "*",
      HttpHeaders.ACCESS_CONTROL_ALLOW_HEADERS, "Origin, Content-Type, Accept, Content-Encoding",
      HttpHeaders.ACCESS_CONTROL_ALLOW_METHODS, "GET, POST, PUT, DELETE, OPTIONS, HEAD");

  @Override
  public void filter(final ContainerRequestContext requestContext, final ContainerResponseContext responseContext) {
    for (final Map.Entry<String, String> entry : MAP.entrySet()) {
      responseContext.getHeaders().add(entry.getKey(), entry.getValue());
    }
  }

}
