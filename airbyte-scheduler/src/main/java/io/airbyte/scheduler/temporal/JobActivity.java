package io.airbyte.scheduler.temporal;

import io.airbyte.config.JobOutput;
import io.airbyte.scheduler.Job;
import io.airbyte.workers.OutputAndStatus;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
public interface JobActivity {
    @ActivityMethod
    OutputAndStatus<JobOutput> run(Job job);
}
