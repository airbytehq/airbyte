package io.airbyte.integrations.destination.bigquery.helpers;

import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LoggerHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(LoggerHelper.class);

  private LoggerHelper() {
  }

  public static void printHeapMemoryConsumption() {
    final int mb = 1024 * 1024;
    final MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
    final long xmx = memoryBean.getHeapMemoryUsage().getMax() / mb;
    final long xms = memoryBean.getHeapMemoryUsage().getInit() / mb;
    LOGGER.info("Initial Memory (xms) mb = {}", xms);
    LOGGER.info("Max Memory (xmx) : mb =  {}", xmx);
  }
}
