/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.version.Version;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.protocol.models.StreamDescriptor;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import javax.annotation.Nullable;

public interface JobCreator {

  /**
   * @param source db model representing where data comes from
   * @param destination db model representing where data goes
   * @param standardSync sync options
   * @param sourceDockerImage docker image to use for the source
   * @param destinationDockerImage docker image to use for the destination
   * @param workspaceId
   * @return the new job if no other conflicting job was running, otherwise empty
   * @throws IOException if something wrong happens
   */
  Optional<Long> createSyncJob(final SourceConnection source, final DestinationConnection destination,final StandardSync standardSync,
                               final String sourceDockerImage,
                               final Version sourceProtocolVersion,
                               final String destinationDockerImage,
                               final Version destinationProtocolVersion,
                               final List<StandardSyncOperation> standardSyncOperations,
                               final @Nullable JsonNode webhookOperationConfigs,
                               final StandardSourceDefinition sourceDefinition,
                               final StandardDestinationDefinition destinationDefinition,
                               final UUID workspaceId)
      throws IOException;

  /**
   *
   * @param destination db model representing where data goes
   * @param standardSync sync options
   * @param destinationDockerImage docker image to use for the destination
   * @param streamsToReset
   * @return the new job if no other conflicting job was running, otherwise empty
   * @throws IOException if something wrong happens
   */
  Optional<Long> createResetConnectionJob(final DestinationConnection destination,
                                          final StandardSync standardSync,
                                          final String destinationDockerImage,
                                          final Version destinationProtocolVersion,
                                          final boolean isCustom,
                                          final List<StandardSyncOperation> standardSyncOperations,
                                          final List<StreamDescriptor> streamsToReset)
      throws IOException;

}
