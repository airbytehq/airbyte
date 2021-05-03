/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.workers.temporal;

import io.temporal.activity.ActivityCancellationType;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.time.Duration;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@WorkflowInterface
public interface TestWorkflow {

  @WorkflowMethod
  String run();

  class WorkflowImpl implements TestWorkflow {

    private static final Logger LOGGER = LoggerFactory.getLogger(WorkflowImpl.class);

    private final ActivityOptions options = ActivityOptions.newBuilder()
        .setScheduleToCloseTimeout(Duration.ofDays(3))
        .setCancellationType(ActivityCancellationType.WAIT_CANCELLATION_COMPLETED)
        .setRetryOptions(TemporalUtils.NO_RETRY)
        .build();

    private final Activity1 activity1 = Workflow.newActivityStub(Activity1.class, options);
    private final Activity2 activity2 = Workflow.newActivityStub(Activity2.class, options);

    @Override
    public String run() {
      final String s1 = activity1.activity1();
      final String s2 = activity2.activity2();

      return "done" + s1 + s2;
    }

  }

  @ActivityInterface
  interface Activity1 {

    @ActivityMethod
    String activity1();

  }

  class Activity1Impl implements Activity1 {

    private static final Logger LOGGER = LoggerFactory.getLogger(Activity1Impl.class);

    private final Consumer<String> thrower;

    public Activity1Impl(Consumer<String> thrower) {
      this.thrower = thrower;
    }

    public String activity1() {
      final String s = "activity1";
      LOGGER.info("before: {}", s);
      thrower.accept(s);
      LOGGER.info("after: {}", s);

      return s;
    }

  }

  @ActivityInterface
  interface Activity2 {

    @ActivityMethod
    String activity2();

  }

  class Activity2Impl implements Activity2 {

    private static final Logger LOGGER = LoggerFactory.getLogger(Activity2Impl.class);

    private final Consumer<String> thrower;

    public Activity2Impl(Consumer<String> thrower) {
      this.thrower = thrower;
    }

    public String activity2() {
      final String s = "activity2";
      LOGGER.info("before: {}", s);
      thrower.accept(s);
      LOGGER.info("after: {}", s);

      return s;
    }

  }

}
