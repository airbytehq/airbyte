/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class FileNodeHandler {

  private final Map<AirbyteStreamNameNamespacePair, Long> fileNodes;
  private final List<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair> failedToQuery;

  public FileNodeHandler() {
    this.fileNodes = new ConcurrentHashMap<>();
    this.failedToQuery = new ArrayList<>();
  }

  public void updateFileNode(final AirbyteStreamNameNamespacePair namespacePair, final Long fileNode) {
    fileNodes.put(namespacePair, fileNode);
  }

  public boolean hasFileNode(final AirbyteStreamNameNamespacePair namespacePair) {
    return fileNodes.containsKey(namespacePair);
  }

  public Long getFileNode(final AirbyteStreamNameNamespacePair namespacePair) {
    return fileNodes.get(namespacePair);
  }

  public void updateFailedToQuery(final io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair namespacePair) {
    failedToQuery.add(namespacePair);
  }

  public List<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair> getFailedToQuery() {
    return Collections.unmodifiableList(failedToQuery);
  }

}
