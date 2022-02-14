/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.cron;

import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@WorkflowInterface
public interface BasicWorkflow {

  Logger LOGGER = LoggerFactory.getLogger(BasicWorkflow.class);
  String WORKFLOW_NAME = "basic-workflow";

  @WorkflowMethod
  String run(String input);

  class BasicWorkflowImpl implements BasicWorkflow {

    private final CountingActivity countingActivity = Workflow.newActivityStub(CountingActivity.class, ActivityConfiguration.LONG_RUN_OPTIONS);

    @Override
    public String run(final String key) {
      LOGGER.debug("workflow running");
      LOGGER.debug("key = " + key);
      countingActivity.incrementCounter(key);
      return key;
    }

  }

  @ActivityInterface
  public interface CountingActivity {

    @ActivityMethod
    void incrementCounter(String key);

  }

  public static class CountingActivityImpl implements CountingActivity {

    private final Map<String, AtomicInteger> counter;

    public CountingActivityImpl(final Map<String, AtomicInteger> counter) {
      this.counter = counter;
    }

    @Override
    public void incrementCounter(final String key) {
      // not actually threadsafe use of the map.
      if (counter.containsKey(key)) {
        counter.get(key).incrementAndGet();
      } else {
        counter.put(key, new AtomicInteger(1));
      }
    }

  }

}
