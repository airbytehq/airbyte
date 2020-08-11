package io.dataline.scheduler;

import io.dataline.api.model.Job;
import io.dataline.api.model.JobAttempt;
import io.dataline.api.model.ScheduleImplementation;
import io.dataline.db.DatabaseHelper;

import java.sql.SQLException;
import java.util.HashSet;
import java.util.Set;

public class Scheduler {
    // todo: make endpoints in the API for reading job state

    public Job getNextJob() {
        // retrieve list of scheduleimplementations + manual jobs and select one to process here
        return null; // todo
    }

    // todo: use a separate enum type for status so it generates nicely
    // todo: use format strings / unix timestamp in java
    public void updateJobStatus(long jobAttemptId, String status) throws SQLException {
        DatabaseHelper.execute("UPDATE job_attempts SET (status = " + status + ", updated_at = (SELECT strftime('%s', 'now'))) WHERE id = " + jobAttemptId + ";");
    }

    public void heartbeat(long jobAttemptId) throws SQLException {
        DatabaseHelper.execute("UPDATE job_attempts SET (last_heartbeat = (SELECT strftime('%s', 'now'))) WHERE id = " + jobAttemptId + ";");
    }

    public void start() {
        // todo:
        // todo: shutdown handler
    }

}
