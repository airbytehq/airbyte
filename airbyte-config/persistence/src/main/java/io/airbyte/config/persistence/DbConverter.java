/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.Tables.CONNECTION;
import static io.airbyte.db.instance.configs.jooq.Tables.WORKSPACE;

import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.Notification;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.Schedule;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.jooq.Record;

public class DbConverter {

  public static StandardSync buildStandardSync(final Record record, final List<UUID> connectionOperationId) throws IOException {
    return new StandardSync()
        .withConnectionId(record.get(CONNECTION.ID))
        .withNamespaceDefinition(
            Enums.toEnum(record.get(CONNECTION.NAMESPACE_DEFINITION, String.class), NamespaceDefinitionType.class)
                .orElseThrow())
        .withNamespaceFormat(record.get(CONNECTION.NAMESPACE_FORMAT))
        .withPrefix(record.get(CONNECTION.PREFIX))
        .withSourceId(record.get(CONNECTION.SOURCE_ID))
        .withDestinationId(record.get(CONNECTION.DESTINATION_ID))
        .withName(record.get(CONNECTION.NAME))
        .withCatalog(
            Jsons.deserialize(record.get(CONNECTION.CATALOG).data(), ConfiguredAirbyteCatalog.class))
        .withStatus(
            record.get(CONNECTION.STATUS) == null ? null : Enums.toEnum(record.get(CONNECTION.STATUS, String.class), Status.class).orElseThrow())
        .withSchedule(Jsons.deserialize(record.get(CONNECTION.SCHEDULE).data(), Schedule.class))
        .withManual(record.get(CONNECTION.MANUAL))
        .withOperationIds(connectionOperationId)
        .withResourceRequirements(Jsons.deserialize(record.get(CONNECTION.RESOURCE_REQUIREMENTS).data(), ResourceRequirements.class));
  }

  public static StandardWorkspace buildStandardWorkspace(final Record record) {
    final List<Notification> notificationList = new ArrayList<>();
    final List fetchedNotifications = Jsons.deserialize(record.get(WORKSPACE.NOTIFICATIONS).data(), List.class);
    for (final Object notification : fetchedNotifications) {
      notificationList.add(Jsons.convertValue(notification, Notification.class));
    }
    return new StandardWorkspace()
        .withWorkspaceId(record.get(WORKSPACE.ID))
        .withName(record.get(WORKSPACE.NAME))
        .withSlug(record.get(WORKSPACE.SLUG))
        .withInitialSetupComplete(record.get(WORKSPACE.INITIAL_SETUP_COMPLETE))
        .withCustomerId(record.get(WORKSPACE.CUSTOMER_ID))
        .withEmail(record.get(WORKSPACE.EMAIL))
        .withAnonymousDataCollection(record.get(WORKSPACE.ANONYMOUS_DATA_COLLECTION))
        .withNews(record.get(WORKSPACE.SEND_NEWSLETTER))
        .withSecurityUpdates(record.get(WORKSPACE.SEND_SECURITY_UPDATES))
        .withDisplaySetupWizard(record.get(WORKSPACE.DISPLAY_SETUP_WIZARD))
        .withTombstone(record.get(WORKSPACE.TOMBSTONE))
        .withNotifications(notificationList)
        .withFirstCompletedSync(record.get(WORKSPACE.FIRST_SYNC_COMPLETE))
        .withFeedbackDone(record.get(WORKSPACE.FEEDBACK_COMPLETE));
  }

}
