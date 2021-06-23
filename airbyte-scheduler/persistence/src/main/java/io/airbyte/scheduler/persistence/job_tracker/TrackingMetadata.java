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

package io.airbyte.scheduler.persistence.job_tracker;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.Job;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.apache.logging.log4j.util.Strings;

public class TrackingMetadata {

  public static ImmutableMap<String, Object> generateSyncMetadata(StandardSync standardSync) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("connection_id", standardSync.getConnectionId());

    final String frequencyString;
    if (standardSync.getManual()) {
      frequencyString = "manual";
    } else {
      final long intervalInMinutes = TimeUnit.SECONDS.toMinutes(ScheduleHelpers.getIntervalInSecond(standardSync.getSchedule()));
      frequencyString = intervalInMinutes + " min";
    }
    metadata.put("frequency", frequencyString);

    final int operationCount = standardSync.getOperationIds() != null ? standardSync.getOperationIds().size() : 0;
    metadata.put("operation_count", operationCount);
    metadata.put("namespace_definition", standardSync.getNamespaceDefinition());
    final boolean isUsingPrefix = standardSync.getPrefix() != null && !standardSync.getPrefix().isBlank();
    metadata.put("table_prefix", isUsingPrefix);

    return metadata.build();
  }

  public static ImmutableMap<String, Object> generateDestinationDefinitionMetadata(StandardDestinationDefinition destinationDefinition) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("connector_destination", destinationDefinition.getName());
    metadata.put("connector_destination_definition_id", destinationDefinition.getDestinationDefinitionId());
    final String imageTag = destinationDefinition.getDockerImageTag();
    if (!Strings.isEmpty(imageTag)) {
      metadata.put("connector_destination_version", imageTag);
    }
    return metadata.build();
  }

  public static ImmutableMap<String, Object> generateSourceDefinitionMetadata(StandardSourceDefinition sourceDefinition) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    metadata.put("connector_source", sourceDefinition.getName());
    metadata.put("connector_source_definition_id", sourceDefinition.getSourceDefinitionId());
    final String imageTag = sourceDefinition.getDockerImageTag();
    if (!Strings.isEmpty(imageTag)) {
      metadata.put("connector_source_version", imageTag);
    }
    return metadata.build();
  }

  public static ImmutableMap<String, Object> generateJobAttemptMetadata(Job job) {
    final Builder<String, Object> metadata = ImmutableMap.builder();
    if (job != null) {
      final List<Attempt> attempts = job.getAttempts();
      if (attempts != null && !attempts.isEmpty()) {
        final Attempt lastAttempt = attempts.get(attempts.size() - 1);
        if (lastAttempt.getOutput() != null && lastAttempt.getOutput().isPresent()) {
          final JobOutput jobOutput = lastAttempt.getOutput().get();
          if (jobOutput.getSync() != null) {
            final StandardSyncSummary syncSummary = jobOutput.getSync().getStandardSyncSummary();
            metadata.put("duration", Math.round((syncSummary.getEndTime() - syncSummary.getStartTime()) / 1000.0));
            metadata.put("volume_mb", syncSummary.getBytesSynced());
            metadata.put("volume_rows", syncSummary.getRecordsSynced());
          }
        }
      }
    }
    return metadata.build();
  }

}
