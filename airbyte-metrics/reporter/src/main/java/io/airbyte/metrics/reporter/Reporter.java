/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import io.airbyte.db.Database;
import io.micronaut.context.event.StartupEvent;
import io.micronaut.runtime.event.annotation.EventListener;
import io.micronaut.scheduling.TaskExecutors;
import io.micronaut.scheduling.TaskScheduler;
import java.time.Duration;
import javax.inject.Inject;
import javax.inject.Named;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Singleton
public class Reporter {

  @Inject
  private Database configDatabase;

  @Inject
  @Named(TaskExecutors.SCHEDULED)
  private TaskScheduler taskScheduler;

  static Database database;

  @EventListener
  @SuppressFBWarnings("ST_WRITE_TO_STATIC_FROM_INSTANCE_METHOD")
  public void onStartup(final StartupEvent startupEvent) {
    // Hack to expose the database connection to the enum. This should be refactored so that each "job"
    // is its
    // own singleton bean that can have the database connection injected into it.
    Reporter.database = configDatabase;
    final var toEmits = ToEmit.values();
    log.info("Scheduling {} metrics for emission...", toEmits.length);
    for (final ToEmit toEmit : toEmits) {
      taskScheduler.scheduleAtFixedRate(Duration.ZERO, Duration.ofMillis(toEmit.timeUnit.toMillis(toEmit.period)), toEmit.emitRunnable);
    }
  }

}
