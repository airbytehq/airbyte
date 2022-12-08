/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import javax.ws.rs.GET;
import javax.ws.rs.Path;

@Path("/api/test")
public class TestController {

  @GET
  public String get() {
    return "test passed - path";
  }

}
