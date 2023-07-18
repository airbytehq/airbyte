/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.List;

public record ParsedCatalog(List<StreamConfig> streams) {

  public StreamConfig getStream(String originalNamespace, String originalName) {
    return streams.stream()
        .filter(s -> s.id().originalNamespace().equals(originalNamespace) && s.id().originalName().equals(originalName))
        .findFirst()
        .orElseThrow(() -> new IllegalArgumentException(String.format(
            "Could not find stream %s.%s out of streams %s",
            originalNamespace,
            originalName,
            streams.stream().map(stream -> stream.id().originalNamespace() + "." + stream.id().originalName()).toList())));
  }

}
