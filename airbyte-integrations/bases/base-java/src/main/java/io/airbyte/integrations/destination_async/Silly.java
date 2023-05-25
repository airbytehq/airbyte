/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;

public class Silly {

  void run() {
    final List<CompletableFuture<Boolean>> running = new ArrayList<>();

    while (true) {

      CompletableFuture.anyOf(running.toArray(new CompletableFuture[0]));
    }
  }

  private Future<Boolean> getNext() {
    return null;
  }

}
