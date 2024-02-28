package io.airbyte.cdk.integrations.source.relationaldb.state;

import java.time.Duration;

public record StateEmitFrequency(long syncCheckpointRecords, Duration syncCheckpointDuration) {}

