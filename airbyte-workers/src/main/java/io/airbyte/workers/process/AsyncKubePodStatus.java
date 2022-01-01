package io.airbyte.workers.process;

import com.google.common.collect.ImmutableList;

import java.util.List;

public enum AsyncKubePodStatus {
    NOT_STARTED, // Pod hasn't been started yet.
    INITIALIZING, // On-start container started but not completed
    RUNNING, // Main container posted running
    FAILED, // Reported status was "failed" or pod was in Error (or other terminal state) without a reported status.
    SUCCEEDED; // Reported status was "success" so both main and on-start succeeded.
}
