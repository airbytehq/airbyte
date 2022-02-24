/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence;

import static org.junit.jupiter.api.Assertions.*;

class ResourceRequirementsUtilsTest {

  // @Test
  // void testNoReqsSet() {
  // final StandardSyncInput input = new StandardSyncInput();
  //
  // final ResourceRequirements sourceReqs = ResourceRequirementsUtils.getResourceRequirements(input,
  // ActorType.SOURCE, JobType.SYNC);
  // final ResourceRequirements destReqs = ResourceRequirementsUtils.getResourceRequirements(input,
  // ActorType.DESTINATION, JobType.SYNC);
  //
  // assertEquals(new ResourceRequirements(), sourceReqs);
  // assertEquals(new ResourceRequirements(), destReqs);
  // }
  //
  // @Test
  // void testDefaultDefinitionReqsSet() {
  // final ResourceRequirements defaultSourceReqs = new ResourceRequirements().withCpuRequest("2");
  // final ResourceRequirements defaultDestReqs = new ResourceRequirements().withCpuRequest("3");
  //
  // final StandardSyncInput input = new StandardSyncInput()
  // .withSourceResourceRequirements(new
  // ActorDefinitionResourceRequirements().withDefault(defaultSourceReqs))
  // .withDestinationResourceRequirements(new
  // ActorDefinitionResourceRequirements().withDefault(defaultDestReqs));
  //
  // final ResourceRequirements sourceReqs = ResourceRequirementsUtils.getResourceRequirements(input,
  // ActorType.SOURCE, JobType.SYNC);
  // final ResourceRequirements destReqs = ResourceRequirementsUtils.getResourceRequirements(input,
  // ActorType.DESTINATION, JobType.SYNC);
  //
  // assertEquals(defaultSourceReqs, sourceReqs);
  // assertEquals(defaultDestReqs, destReqs);
  // }
  //
  // @Test
  // void testJobSpecificResourceRequirementsOverrideDefault() {
  // final ResourceRequirements defaultReqs = new
  // ResourceRequirements().withCpuRequest("2").withMemoryRequest("300Mi");
  // final JobTypeResourceLimit jobTypeResourceLimit = new
  // JobTypeResourceLimit().withJobType(JobType.SYNC).withResourceRequirements(
  // new ResourceRequirements().withCpuRequest("4").withMemoryLimit("500Mi"));
  // final StandardSyncInput input = new StandardSyncInput()
  // .withSourceResourceRequirements(new ActorDefinitionResourceRequirements()
  // .withDefault(defaultReqs)
  // .withJobSpecific(List.of(jobTypeResourceLimit)))
  // .withDestinationResourceRequirements(new ActorDefinitionResourceRequirements()
  // .withDefault(defaultReqs)
  // .withJobSpecific(List.of(jobTypeResourceLimit)));
  //
  // final ResourceRequirements sourceReqs = ResourceRequirementsUtils.getResourceRequirements(input,
  // ActorType.SOURCE, JobType.SYNC);
  // final ResourceRequirements destReqs = ResourceRequirementsUtils.getResourceRequirements(input,
  // ActorType.DESTINATION, JobType.SYNC);
  //
  // final ResourceRequirements expectedReqs = new ResourceRequirements()
  // .withCpuRequest("4")
  // .withMemoryRequest("300Mi")
  // .withMemoryLimit("500Mi");
  // assertEquals(expectedReqs, sourceReqs);
  // assertEquals(expectedReqs, destReqs);
  // }
  //
  // @Test
  // void testConnectionResourceRequirementsOverrideDefault() {
  // final ResourceRequirements defaultReqs = new
  // ResourceRequirements().withCpuRequest("2").withMemoryRequest("300Mi");
  // final JobTypeResourceLimit jobTypeResourceLimit = new
  // JobTypeResourceLimit().withJobType(JobType.SYNC).withResourceRequirements(
  // new ResourceRequirements().withCpuRequest("3").withCpuLimit("4"));
  // final ResourceRequirements connectionResourceReqs = new
  // ResourceRequirements().withCpuLimit("5").withMemoryLimit("400Mi");
  // final StandardSyncInput input = new StandardSyncInput()
  // .withSourceResourceRequirements(new ActorDefinitionResourceRequirements()
  // .withDefault(defaultReqs)
  // .withJobSpecific(List.of(jobTypeResourceLimit)))
  // .withDestinationResourceRequirements(new ActorDefinitionResourceRequirements()
  // .withDefault(defaultReqs)
  // .withJobSpecific(List.of(jobTypeResourceLimit)))
  // .withResourceRequirements(connectionResourceReqs);
  //
  // final ResourceRequirements sourceReqs = ResourceRequirementsUtils.getResourceRequirements(input,
  // ActorType.SOURCE, JobType.SYNC);
  // final ResourceRequirements destReqs = ResourceRequirementsUtils.getResourceRequirements(input,
  // ActorType.DESTINATION, JobType.SYNC);
  //
  // final ResourceRequirements expectedReqs = new ResourceRequirements()
  // .withCpuRequest("3")
  // .withCpuLimit("5")
  // .withMemoryRequest("300Mi")
  // .withMemoryLimit("400Mi");
  // assertEquals(expectedReqs, sourceReqs);
  // assertEquals(expectedReqs, destReqs);
  // }

}
