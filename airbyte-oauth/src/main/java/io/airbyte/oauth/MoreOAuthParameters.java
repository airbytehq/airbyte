/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import java.util.Comparator;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Stream;

public class MoreOAuthParameters {

  public static Optional<SourceOAuthParameter> getSourceOAuthParameter(
                                                                       Stream<SourceOAuthParameter> stream,
                                                                       UUID workspaceId,
                                                                       UUID sourceDefinitionId) {
    return stream
        .filter(p -> sourceDefinitionId.equals(p.getSourceDefinitionId()))
        .filter(p -> p.getWorkspaceId() == null || workspaceId.equals(p.getWorkspaceId()))
        // we prefer params specific to a workspace before global ones (ie workspace is null)
        .min(Comparator.comparing(SourceOAuthParameter::getWorkspaceId, Comparator.nullsLast(Comparator.naturalOrder()))
            .thenComparing(SourceOAuthParameter::getOauthParameterId));
  }

  public static Optional<DestinationOAuthParameter> getDestinationOAuthParameter(
                                                                                 Stream<DestinationOAuthParameter> stream,
                                                                                 UUID workspaceId,
                                                                                 UUID destinationDefinitionId) {
    return stream
        .filter(p -> destinationDefinitionId.equals(p.getDestinationDefinitionId()))
        .filter(p -> p.getWorkspaceId() == null || workspaceId.equals(p.getWorkspaceId()))
        // we prefer params specific to a workspace before global ones (ie workspace is null)
        .min(Comparator.comparing(DestinationOAuthParameter::getWorkspaceId, Comparator.nullsLast(Comparator.naturalOrder()))
            .thenComparing(DestinationOAuthParameter::getOauthParameterId));
  }

}
