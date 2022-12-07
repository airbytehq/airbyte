/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.micronaut.runtime.Micronaut;

public class Application {

  public static void main(final String[] args) {
    Micronaut
        .build(args)
        // Lazy initialization can make the first requests to be slow
        .eagerInitSingletons(true)
        .mainClass(Application.class)
        .start();
  }

}
