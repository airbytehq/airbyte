/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Get;
import io.micronaut.http.annotation.Produces;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;
import java.util.Map;

/**
 * Creates a controller that returns a 200 JSON response on any path requested.
 * <p>
 * This is intended to stay up as long as the Kube worker exists so pods spun up can check if the
 * spawning Kube worker still exists.
 */
// @TODO remove this annotation
@Secured(SecurityRule.IS_ANONYMOUS)
@Controller
public class HeartbeatController {

  private static final Map<String, Object> response = Map.of("up", true);

  @Get
  @Produces(MediaType.APPLICATION_JSON)
  public Map<String, Object> get() {
    return response;
  }

}
