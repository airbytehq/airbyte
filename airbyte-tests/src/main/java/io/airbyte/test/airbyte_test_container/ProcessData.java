/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.airbyte_test_container;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.workers.process.KubePodProcess;
import io.airbyte.workers.process.KubePortManagerSingleton;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
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

    final var dataFile = Path.of("./bin/data-dev-1-kube-pod-process.txt");
    final var lines = Files.lines(dataFile).collect(Collectors.toList());

    final List<Long> timesToSchedule = new ArrayList<>();
    final List<Long> timesToInit = new ArrayList<>();
    final List<Long> timesToContainerReady = new ArrayList<>();
    final List<Long> timesToReady = new ArrayList<>();

    int processed = 0;
    int ignored = 0;

    final Set<String> seenEntries = new HashSet<>();

    for (final String line : lines) {
      try {
        final var json = jackson.readTree(line);
        if (json.has("creationTimestamp") && json.has("conditions")) {
          final var name = json.get("name").asText();
          if (seenEntries.contains(name)) {
            ignored++;
            continue;
          }

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
          seenEntries.add(name);
        }
      } catch (final Exception e) {}
    }

    log.info("Processed lines: {}, Ignored lines: {}", processed, ignored);
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
    final var totalAvg = scheduleAvg + initAvg + containerReadyAvg + readyAvg;
    final var total95Percentile = schedule95Percentile + init95Percentile + containerReady95Percentile + ready95Percentile;
    log.info("overall average: {}, overall 95 percentile: {}", totalAvg, total95Percentile);
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
