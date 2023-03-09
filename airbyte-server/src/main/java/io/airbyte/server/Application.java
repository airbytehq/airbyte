/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.micronaut.runtime.Micronaut;

public class Application {

  public static void main(final String[] args) {
    Micronaut.run(Application.class, args);
  }

}
