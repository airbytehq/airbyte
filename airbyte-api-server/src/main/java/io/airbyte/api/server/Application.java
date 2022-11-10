/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.server;

import dev.speakeasyapi.micronaut.EnableSpeakeasyInterceptor;
import dev.speakeasyapi.micronaut.SpeakeasyFilter;
import io.micronaut.context.annotation.Import;
import io.micronaut.runtime.Micronaut;

@Import(classes = { SpeakeasyFilter.class, EnableSpeakeasyInterceptor.class }, annotated = "*")
public class Application {

  public static void main(final String[] args) {
    if (args.length > 1) {
      EnableSpeakeasyInterceptor.configure(
          args[0],
          args[1]
      );
    }

    Micronaut.run(Application.class, args);
  }

}
