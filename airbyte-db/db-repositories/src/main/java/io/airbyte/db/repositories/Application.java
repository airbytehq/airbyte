/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.repositories;

import io.micronaut.runtime.Micronaut;
import jakarta.inject.Singleton;

@Singleton
public class Application {

  public static void main(final String[] args) {
    Micronaut.run(Application.class, args);
  }

}
