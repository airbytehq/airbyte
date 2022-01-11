/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.airbyte_test_container;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.joda.time.DateTime;
import org.joda.time.Period;
import org.joda.time.format.ISODateTimeFormat;

@Slf4j
public class ProcessData {

  public static void main(final String[] args) throws IOException {
    log.info("running!");

    final var jackson = new ObjectMapper();

    final var dataFile = Path.of("./bin/data.txt");
    final var lines = Files.lines(dataFile).collect(Collectors.toList());

    final List<Long> timesToSchedule = new ArrayList<>();
    final List<Long> timesToInit = new ArrayList<>();
    final List<Long> timesToContainerReady = new ArrayList<>();
    final List<Long> timesToReady = new ArrayList<>();

    int processed = 0;

    for (final String line : lines) {
      try {
        final var json = jackson.readTree(line);
        if (json.has("creationTimestamp") && json.has("conditions")) {
          final var createTs = DateTime.parse(json.get("creationTimestamp").asText());

          final var conditions = json.get("conditions");
          final var scheduledTs = DateTime.parse(conditions.get("PodScheduled").asText());
          final var initTs = DateTime.parse(conditions.get("Initialized").asText());
          final var containerReadyTs = DateTime.parse(conditions.get("ContainersReady").asText());
          final var readyTs = DateTime.parse(conditions.get("Ready").asText());

          final var timeToSchedule = new Period(createTs, scheduledTs);
          final var timeToInit = new Period(scheduledTs, initTs);
          final var timeToContainerReady = new Period(initTs, containerReadyTs);
          final var timeToReady = new Period(containerReadyTs, readyTs);

          timesToSchedule.add((long) timeToSchedule.getSeconds());
          timesToInit.add((long) timeToInit.getSeconds());
          timesToContainerReady.add((long) timeToContainerReady.getSeconds());
          timesToReady.add((long) timeToReady.getSeconds());

          processed++;
        }
      } catch (final Exception e) {}
    }

    log.info("scheduling time - average: {}, 95 percentile: {}", average(timesToSchedule), percentile(timesToSchedule, 95));
    log.info("init time - average: {}, 95 percentile: {}", average(timesToInit), percentile(timesToInit, 95));
    log.info("container ready time - average: {}, 95 percentile: {}", average(timesToContainerReady), percentile(timesToContainerReady, 95));
    log.info("ready time - average: {}, 95 percentile: {}", average(timesToReady), percentile(timesToReady, 95));
    log.info("Processed lines: {}", processed);
  }

  public static long percentile(final List<Long> latencies, final double percentile) {
    Collections.sort(latencies);
    final int index = (int) Math.ceil(percentile / 100.0 * latencies.size());
    return latencies.get(index-1);
  }

  public static double average(final List<Long> latencies) {
    double total = 0;
    for (final Long a : latencies) {
      total += a;
    }
    return total/latencies.size();
  }
}
