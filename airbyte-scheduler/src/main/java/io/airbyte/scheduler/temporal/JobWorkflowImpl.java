package io.airbyte.scheduler.temporal;

import io.airbyte.scheduler.Job;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;

import java.time.Duration;

public class JobWorkflowImpl implements JobWorkflow {
    ActivityOptions options = ActivityOptions.newBuilder()
            .setScheduleToCloseTimeout(Duration.ofMinutes(2)) // todo
            .build();

    private final JobActivity jobActivity = Workflow.newActivityStub(JobActivity.class, options);

    @Override
    public void run(Job job) {
        jobActivity.run(job);
    }
}
