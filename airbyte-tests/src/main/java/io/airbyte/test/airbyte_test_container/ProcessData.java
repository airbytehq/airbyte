/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.airbyte_test_container;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;
import org.joda.time.DateTime;
import org.joda.time.Period;

@Slf4j
public class ProcessData {

  public static void main(final String[] args) throws IOException {
    log.info("running!");

    final var jackson = new ObjectMapper();

    final var dataFile = Path.of("./bin/dev-1-within-kube-pod-process-0.2-1-sec-init.txt");
    final var lines = Files.lines(dataFile).collect(Collectors.toList());

    final List<Long> timesToSchedule = new ArrayList<>();
    final List<Long> timesToInit = new ArrayList<>();
    final List<Long> timesToContainerReady = new ArrayList<>();
    final List<Long> timesToReady = new ArrayList<>();

    final List<Long> timesToRun = new ArrayList<>();
    final List<Long> totalTimeTaken = new ArrayList<>();

    int processed = 0;
    int ignored = 0;

    final Set<String> seenEntries = new HashSet<>();

    for (final String line : lines) {
      try {
        final var json = jackson.readTree(line);
        // Processing pod creation data set.
        final var createTs = DateTime.parse(json.get("creationTimestamp").asText());
        final var name = json.get("name").asText();

        if (seenEntries.contains(name) || name.contains("sweeper") || name.contains("airbyte")) {
          ignored++;
          continue;
        }

        if (json.has("conditions")) {

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
        }
        // Processing successful pod data set.
        if (json.has("mainStartTimestamp")) {
          // Add one second since the Kube watch api 'succeeded' event rounds down, while the 'running' event
          // rounds up. Round up to standardise.
          final var mainStartTs = DateTime.parse(json.get("mainStartTimestamp").asText()).plusSeconds(1);
          final var mainFinishTs = DateTime.parse(json.get("mainFinishTimestamp").asText()).plusSeconds(1);

          final var timeToRun = new Period(mainStartTs, mainFinishTs);
          timesToRun.add((long) timeToRun.getSeconds());

          final var totalTime = new Period(createTs, mainFinishTs);
          totalTimeTaken.add((long) totalTime.getSeconds());
        }

        processed++;
        seenEntries.add(name);

      } catch (final Exception e) {
        log.error("error: ", e);
      }
    }

    log.info("Processed lines: {}, Ignored lines: {}", processed, ignored);
    if (timesToSchedule.size() > 0) {
      final var scheduleAvg = average(timesToSchedule);
      final var schedule95Percentile = percentile(timesToSchedule, 95);
      log.info("scheduling time - average: {}, 95 percentile: {}", scheduleAvg, schedule95Percentile);

      final var initAvg = average(timesToInit);
      final var init95Percentile = percentile(timesToInit, 95);
      log.info("init time - average: {}, 95 percentile: {}", initAvg, init95Percentile);

      final var containerReadyAvg = average(timesToContainerReady);
      final var containerReady95Percentile = percentile(timesToContainerReady, 95);
      log.info("container ready time - average: {}, 95 percentile: {}", containerReadyAvg, containerReady95Percentile);

      final var readyAvg = average(timesToReady);
      final var ready95Percentile = percentile(timesToReady, 95);
      log.info("ready time - average: {}, 95 percentile: {}", readyAvg, ready95Percentile);

      log.info("");
      final var totalStartAvg = scheduleAvg + initAvg + containerReadyAvg + readyAvg;
      final var totalStart95Percentile = schedule95Percentile + init95Percentile + containerReady95Percentile + ready95Percentile;
      log.info("overall start average: {}, overall start 95 percentile: {}", totalStartAvg, totalStart95Percentile);
    } else {
      final var runAvg = average(timesToRun);
      final var run99Percentile = percentile(timesToRun, 99);
      log.info("run average: {}, run 99 percentile: {}", runAvg, run99Percentile);

      final var totalTimeAvg = average(totalTimeTaken);
      final var totalTime99Percentile = percentile(totalTimeTaken, 99);
      log.info("overall average: {}, overall 99 percentile: {}", totalTimeAvg, totalTime99Percentile);
    }
  }

  public static long percentile(final List<Long> latencies, final double percentile) {
    Collections.sort(latencies);
    final int index = (int) Math.ceil(percentile / 100.0 * latencies.size());
    return latencies.get(index - 1);
  }

  public static double average(final List<Long> latencies) {
    double total = 0;
    for (final Long a : latencies) {
      total += a;
    }
    return total / latencies.size();
  }

}
