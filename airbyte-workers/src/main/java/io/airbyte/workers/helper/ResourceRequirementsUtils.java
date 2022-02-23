/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import com.google.common.base.Preconditions;
import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.ActorType;
import io.airbyte.config.JobTypeResourceLimit;
import io.airbyte.config.JobTypeResourceLimit.JobType;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.workers.WorkerConfigs;
import java.util.ArrayList;
import java.util.Collections;
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
  public static ResourceRequirements getResourceRequirements(final StandardSyncInput input,
                                                             final ActorType actorType,
                                                             final JobType jobType,
                                                             final WorkerConfigs workerConfigs) {
    final ActorDefinitionResourceRequirements actorDefResourceReqs = getResourceRequirementsForActorType(input, actorType);
    final ResourceRequirements jobTypeResourceReqs = getResourceRequirementsForJobType(actorDefResourceReqs, jobType).orElse(null);
    return mergeResourceRequirements(input.getResourceRequirements(), jobTypeResourceReqs, workerConfigs.getResourceRequirements());
  }

  /**
   * Given a list of resource requirements, merges them together. Earlier reqs override later ones.
   *
   * @param resourceReqs - list of resource request to merge
   * @return merged resource req
   */
  public static ResourceRequirements mergeResourceRequirements(final ResourceRequirements... resourceReqs) {
    final ResourceRequirements outputReqs = new ResourceRequirements();
    final List<ResourceRequirements> reversed = new ArrayList<>(List.of(resourceReqs));
    Collections.reverse(reversed);

    for (final ResourceRequirements resourceReq : reversed) {
      if (resourceReq == null) {
        continue;
      }

      if (resourceReq.getCpuRequest() != null) {
        outputReqs.setCpuRequest(resourceReq.getCpuRequest());
      }
      if (resourceReq.getCpuLimit() != null) {
        outputReqs.setCpuLimit(resourceReq.getCpuLimit());
      }
      if (resourceReq.getMemoryRequest() != null) {
        outputReqs.setMemoryRequest(resourceReq.getMemoryRequest());
      }
      if (resourceReq.getMemoryLimit() != null) {
        outputReqs.setMemoryLimit(resourceReq.getMemoryLimit());
      }
    }
    return outputReqs;
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
