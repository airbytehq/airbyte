/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers.helpers;

import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionSearch;
import io.airbyte.api.model.ConnectionStatus;
import java.util.UUID;
import org.apache.logging.log4j.util.Strings;

public class ConnectionMatcher implements Matchable<ConnectionRead> {

  private final ConnectionSearch search;

  public ConnectionMatcher(final ConnectionSearch search) {
    this.search = search;
  }

  @Override
  public ConnectionRead match(final ConnectionRead query) {
    if (search == null) {
      return query;
    }

    final UUID connectionId = search.getConnectionId() == null ? query.getConnectionId() : search.getConnectionId();
    final ConnectionStatus connectionStatus = search.getStatus() == null ? query.getStatus() : search.getStatus();
    final UUID destinationId = search.getDestinationId() == null ? query.getDestinationId() : search.getDestinationId();
    final String name = Strings.isBlank(search.getName()) ? query.getName() : search.getName();
    final UUID sourceId = search.getSourceId() == null ? query.getSourceId() : search.getSourceId();

    final ConnectionRead fromSearch = new ConnectionRead()
        .connectionId(connectionId)
        .name(name)
        .sourceId(sourceId)
        .destinationId(destinationId)
        .syncCatalog(query.getSyncCatalog())
        .status(connectionStatus);
    fromSearch.namespaceFormat(Strings.isBlank(search.getNamespaceFormat()) || search.getNamespaceFormat().equals("null")
        ? query.getNamespaceFormat()
        : search.getNamespaceFormat());
    fromSearch.namespaceDefinition(
        search.getNamespaceDefinition() == null ? query.getNamespaceDefinition() : search.getNamespaceDefinition());
    fromSearch.prefix(Strings.isBlank(search.getPrefix()) ? query.getPrefix() : search.getPrefix());
    fromSearch.schedule(search.getSchedule() == null ? query.getSchedule() : search.getSchedule());

    // these properties are not enabled in the search
    fromSearch.resourceRequirements(query.getResourceRequirements());
    fromSearch.operationIds(query.getOperationIds());

    return fromSearch;
  }

}
