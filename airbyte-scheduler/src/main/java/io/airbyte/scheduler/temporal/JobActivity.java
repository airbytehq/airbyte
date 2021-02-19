package io.airbyte.scheduler.temporal;

import io.airbyte.scheduler.Job;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
public interface JobActivity {
    @ActivityMethod
    void run(Job job);
}
