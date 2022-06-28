/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.client.EventRunner;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ServerAppTest {

  @Mock
  private ConfigRepository mConfigRepository;

  @Mock
  private JobPersistence mJobPersistence;

  @Mock
  private EventRunner mEventRunner;

  @Test
  void testMigrationAlreadyPerformed() throws Exception {
    when(mJobPersistence.isSchedulerMigrated()).thenReturn(true);

    ServerApp.migrateExistingConnectionsToTemporalScheduler(mConfigRepository, mJobPersistence, mEventRunner);

    verifyNoMoreInteractions(mJobPersistence);
    verifyNoMoreInteractions(mConfigRepository);
    verifyNoMoreInteractions(mEventRunner);
  }

  @Test
  void testPerformMigration() throws Exception {
    when(mJobPersistence.isSchedulerMigrated()).thenReturn(false);

    final StandardSync activeConnection = new StandardSync().withStatus(Status.ACTIVE).withConnectionId(UUID.randomUUID());
    final StandardSync inactiveConnection = new StandardSync().withStatus(Status.INACTIVE).withConnectionId(UUID.randomUUID());
    final StandardSync deprecatedConnection = new StandardSync().withStatus(Status.DEPRECATED).withConnectionId(UUID.randomUUID());
    when(mConfigRepository.listStandardSyncs()).thenReturn(List.of(activeConnection, inactiveConnection, deprecatedConnection));

    ServerApp.migrateExistingConnectionsToTemporalScheduler(mConfigRepository, mJobPersistence, mEventRunner);

    verify(mEventRunner).migrateSyncIfNeeded(Set.of(activeConnection.getConnectionId(), inactiveConnection.getConnectionId()));
    verify(mJobPersistence).setSchedulerMigrationDone();
    verifyNoMoreInteractions(mJobPersistence);
    verifyNoMoreInteractions(mConfigRepository);
    verifyNoMoreInteractions(mEventRunner);
  }

}
