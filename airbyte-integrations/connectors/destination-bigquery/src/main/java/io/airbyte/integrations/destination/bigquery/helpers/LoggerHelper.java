/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.helpers;

import com.google.cloud.bigquery.BigQueryError;
import com.google.cloud.bigquery.Job;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.util.List;
import java.util.stream.Collectors;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LoggerHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(LoggerHelper.class);

  private LoggerHelper() {}

  public static void printHeapMemoryConsumption() {
    final int mb = 1024 * 1024;
    final MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
    final long xmx = memoryBean.getHeapMemoryUsage().getMax() / mb;
    final long xms = memoryBean.getHeapMemoryUsage().getInit() / mb;
    LOGGER.info("Initial Memory (xms) mb = {}", xms);
    LOGGER.info("Max Memory (xmx) : mb =  {}", xmx);
  }

  public static String getJobErrorMessage(List<BigQueryError> errors, Job job) {
    if (!errors.isEmpty()) {
      return String.format("Error is happened during execution for job: %s, \n For more details see Big Query Error collection: %s:", job,
          errors.stream().map(BigQueryError::toString).collect(Collectors.joining(",\n ")));
    }
    return StringUtils.EMPTY;
  }

}
