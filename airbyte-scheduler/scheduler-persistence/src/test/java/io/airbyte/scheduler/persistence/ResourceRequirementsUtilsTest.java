/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.JobTypeResourceLimit;
import io.airbyte.config.JobTypeResourceLimit.JobType;
import io.airbyte.config.ResourceRequirements;
import java.util.List;
import org.junit.jupiter.api.Test;

class ResourceRequirementsUtilsTest {

  private static final String FIVE_HUNDRED_MEM = "500Mi";

  @Test
  void testNoReqsSet() {
    final ResourceRequirements result = ResourceRequirementsUtils.getResourceRequirements(
        null,
        null,
        null,
        JobType.SYNC);

    assertEquals(new ResourceRequirements(), result);
  }

  @Test
  void testWorkerDefaultReqsSet() {
    final ResourceRequirements workerDefaultReqs = new ResourceRequirements().withCpuRequest("1").withCpuLimit("1");
    final ResourceRequirements reqs = ResourceRequirementsUtils.getResourceRequirements(
        null,
        null,
        workerDefaultReqs,
        JobType.SYNC);

    assertEquals(workerDefaultReqs, reqs);
  }

  @Test
  void testDefinitionDefaultReqsOverrideWorker() {
    final ResourceRequirements workerDefaultReqs = new ResourceRequirements().withCpuRequest("1").withCpuLimit("1");
    final ResourceRequirements definitionDefaultReqs = new ResourceRequirements().withCpuLimit("2").withMemoryRequest("100Mi");
    final ActorDefinitionResourceRequirements definitionReqs = new ActorDefinitionResourceRequirements().withDefault(definitionDefaultReqs);

    final ResourceRequirements result = ResourceRequirementsUtils.getResourceRequirements(
        null,
        definitionReqs,
        workerDefaultReqs,
        JobType.SYNC);

    final ResourceRequirements expectedReqs = new ResourceRequirements()
        .withCpuRequest("1")
        .withCpuLimit("2")
        .withMemoryRequest("100Mi");

    assertEquals(expectedReqs, result);
  }

  @Test
  void testJobSpecificReqsOverrideDefault() {
    final ResourceRequirements workerDefaultReqs = new ResourceRequirements().withCpuRequest("1").withCpuLimit("1");
    final ResourceRequirements definitionDefaultReqs = new ResourceRequirements().withCpuLimit("2").withMemoryRequest("100Mi");
    final JobTypeResourceLimit jobTypeResourceLimit = new JobTypeResourceLimit().withJobType(JobType.SYNC).withResourceRequirements(
        new ResourceRequirements().withCpuRequest("2").withMemoryRequest("200Mi").withMemoryLimit("300Mi"));
    final ActorDefinitionResourceRequirements definitionReqs = new ActorDefinitionResourceRequirements()
        .withDefault(definitionDefaultReqs)
        .withJobSpecific(List.of(jobTypeResourceLimit));

    final ResourceRequirements result = ResourceRequirementsUtils.getResourceRequirements(
        null,
        definitionReqs,
        workerDefaultReqs,
        JobType.SYNC);

    final ResourceRequirements expectedReqs = new ResourceRequirements()
        .withCpuRequest("2")
        .withCpuLimit("2")
        .withMemoryRequest("200Mi")
        .withMemoryLimit("300Mi");
    assertEquals(expectedReqs, result);
  }

  @Test
  void testConnectionResourceRequirementsOverrideDefault() {
    final ResourceRequirements workerDefaultReqs = new ResourceRequirements().withCpuRequest("1");
    final ResourceRequirements definitionDefaultReqs = new ResourceRequirements().withCpuLimit("2").withCpuRequest("2");
    final JobTypeResourceLimit jobTypeResourceLimit = new JobTypeResourceLimit().withJobType(JobType.SYNC).withResourceRequirements(
        new ResourceRequirements().withCpuLimit("3").withMemoryRequest("200Mi"));
    final ActorDefinitionResourceRequirements definitionReqs = new ActorDefinitionResourceRequirements()
        .withDefault(definitionDefaultReqs)
        .withJobSpecific(List.of(jobTypeResourceLimit));
    final ResourceRequirements connectionResourceRequirements =
        new ResourceRequirements().withMemoryRequest("400Mi").withMemoryLimit(FIVE_HUNDRED_MEM);

    final ResourceRequirements result = ResourceRequirementsUtils.getResourceRequirements(
        connectionResourceRequirements,
        definitionReqs,
        workerDefaultReqs,
        JobType.SYNC);

    final ResourceRequirements expectedReqs = new ResourceRequirements()
        .withCpuRequest("2")
        .withCpuLimit("3")
        .withMemoryRequest("400Mi")
        .withMemoryLimit(FIVE_HUNDRED_MEM);
    assertEquals(expectedReqs, result);
  }

  @Test
  void testConnectionResourceRequirementsOverrideWorker() {
    final ResourceRequirements workerDefaultReqs = new ResourceRequirements().withCpuRequest("1").withCpuLimit("1");
    final ResourceRequirements connectionResourceRequirements = new ResourceRequirements().withCpuLimit("2").withMemoryLimit(FIVE_HUNDRED_MEM);

    final ResourceRequirements result = ResourceRequirementsUtils.getResourceRequirements(connectionResourceRequirements, workerDefaultReqs);

    final ResourceRequirements expectedReqs = new ResourceRequirements()
        .withCpuRequest("1")
        .withCpuLimit("2")
        .withMemoryLimit(FIVE_HUNDRED_MEM);
    assertEquals(expectedReqs, result);
  }

}
