/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import com.google.common.base.Preconditions;
import io.airbyte.config.ActorDefinition.ActorType;
import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.JobTypeResourceLimit;
import io.airbyte.config.JobTypeResourceLimit.JobType;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSyncInput;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class ResourceRequirementsUtils {

  /**
   * Given an actor type and job type, returns resource requirements, if present. Otherwise, null.
   * Sync-level resource requirements, take precedence over connector definition level ones.
   *
   * @param input - sync input
   * @param actorType - type of actor to extract resource requirements for
   * @param jobType - toe of job to extract resource requirements for
   * @return resource requirements, if present, otherwise null.
   */
  public static ResourceRequirements getResourceRequirements(final StandardSyncInput input, final ActorType actorType, final JobType jobType) {
    final ActorDefinitionResourceRequirements actorDefResourceReqs = getResourceRequirementsForActorType(input, actorType);
    if (input.getResourceRequirements() != null) {
      return input.getResourceRequirements();
    } else if (actorDefResourceReqs != null) {
      final Optional<ResourceRequirements> resourceRequirementsForJobType = getResourceRequirementsForJobType(actorDefResourceReqs, jobType);
      return resourceRequirementsForJobType.orElse(actorDefResourceReqs.getDefault()); // default can return null.
    } else {
      return null;
    }

  }

  private static Optional<ResourceRequirements> getResourceRequirementsForJobType(final ActorDefinitionResourceRequirements actorDefResourceReqs,
                                                                                  final JobType jobType) {
    final List<ResourceRequirements> jobTypeResourceRequirement = actorDefResourceReqs.getJobSpecific()
        .stream()
        .filter(jobSpecific -> jobSpecific.getJobType() == jobType).map(JobTypeResourceLimit::getResourceRequirements).collect(
            Collectors.toList());

    Preconditions.checkArgument(jobTypeResourceRequirement.size() <= 1, "Should only have one resource requirement per job type.");
    return jobTypeResourceRequirement.isEmpty() ? Optional.empty() : Optional.of(jobTypeResourceRequirement.get(0));
  }

  private static ActorDefinitionResourceRequirements getResourceRequirementsForActorType(final StandardSyncInput input, final ActorType actorType) {
    switch (actorType) {
      case SOURCE -> {
        return input.getSourceResourceRequirements();
      }
      case DESTINATION -> {
        return input.getDestinationResourceRequirements();
      }
      default -> {
        throw new IllegalArgumentException("Unrecognized actor type.");
      }
    }
  }

}
