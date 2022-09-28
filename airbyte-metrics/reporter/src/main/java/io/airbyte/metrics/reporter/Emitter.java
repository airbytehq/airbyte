package io.airbyte.metrics.reporter;

import io.airbyte.db.Database;
import io.airbyte.metrics.lib.MetricAttribute;
import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.MetricQueries;
import io.airbyte.metrics.lib.MetricTags;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import jakarta.inject.Singleton;
import java.lang.invoke.MethodHandles;
import java.time.Duration;
import java.util.concurrent.Callable;
import java.util.concurrent.TimeUnit;
import javax.xml.crypto.Data;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract sealed class Emitter {
  protected static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());
  protected static final long DEFAULT_PERIOD = 15;
  protected static final TimeUnit DEFAULT_TIME_UNIT = TimeUnit.SECONDS;
  protected final Callable<Void> callable;
  Emitter(final Callable<Void> callable) {
    this.callable = callable;
  }

  public void Emit() {
    try {
      callable.call();
    } catch (final Exception e) {
      log.error("Exception querying database for metric: ", e);
    }
  }

  public Duration getDuration() {
    return Duration.ofSeconds(15);
  }

  private Runnable countMetricEmission(final Callable<Void> metricQuery) {
    return () -> {
      try {
        metricQuery.call();
      } catch (final Exception e) {
        log.error("Exception querying database for metric: ", e);
      }
    };
  }
}

@Singleton
final class NumPendingJobs extends Emitter {
  public NumPendingJobs(final MetricClient client, final Database db) {
    super(() -> {
      final var pending = db.query(MetricQueries::numberOfPendingJobs);
      client.gauge(OssMetricsRegistry.NUM_PENDING_JOBS, pending);
      return null;
    });
  }
}

@Singleton
final class NumRunningJobs extends Emitter {
  public NumRunningJobs(final MetricClient client, final Database db) {
    super(() -> {
      final var running = db.query(MetricQueries::numberOfRunningJobs);
      client.gauge(OssMetricsRegistry.NUM_RUNNING_JOBS, running);
      return null;
    });
  }
}

@Singleton
final class OverallJobRuntimeInLastHourByTerminalStateSeconds extends Emitter {
  public OverallJobRuntimeInLastHourByTerminalStateSeconds(final MetricClient client, final Database db) {
    super(() -> {
      final var times = db.query(MetricQueries::overallJobRuntimeForTerminalJobsInLastHour);
      times.forEach(pair -> client.distribution(
          OssMetricsRegistry.OVERALL_JOB_RUNTIME_IN_LAST_HOUR_BY_TERMINAL_STATE_SECS,
          pair.getRight(),
          new MetricAttribute(MetricTags.JOB_STATUS, MetricTags.getJobStatus(pair.getLeft()))
      ));
      return null;
    });
  }

  @Override
  public Duration getDuration() {
    return Duration.ofHours(1);
  }
}