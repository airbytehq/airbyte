/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.support;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;

import io.airbyte.workers.temporal.stubs.TestActivity;
import io.airbyte.workers.temporal.sync.RouterService;
import io.temporal.activity.ActivityOptions;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link MultiCloudTemporalActivityStubGeneratorFunction} class.
 */
class MultiCloudTemporalActivityStubGeneratorFunctionTest {

  @Test
  void testActivityStubGenerationForControlPane() {
    final ActivityOptions activityOptions = mock(ActivityOptions.class);
    final TestActivity testActivity = mock(TestActivity.class);
    final RouterService routerService = mock(RouterService.class);
    final TemporalActivityStubGenerationOptions options =
        new TemporalActivityStubGenerationOptions(activityOptions, testActivity.getClass(), null, null);
    final MultiCloudTemporalActivityStubGeneratorFunction generatorFunction = spy(new MultiCloudTemporalActivityStubGeneratorFunction());
    doReturn(testActivity).when(generatorFunction).generateActivityStub(any(), any());
    generatorFunction.setRouterService(routerService);

    final Object result = generatorFunction.apply(options);
    assertEquals(testActivity, result);
  }

  @Test
  void testActivityStubGenerationForDataPlane() {
    final ActivityOptions activityOptions = mock(ActivityOptions.class);
    final TestActivity testActivity = mock(TestActivity.class);
    final RouterService routerService = mock(RouterService.class);
    final String workflowVersionChangeId = "test";
    final UUID connectionId = UUID.randomUUID();
    final TemporalActivityStubGenerationOptions options =
        new TemporalActivityStubGenerationOptions(activityOptions, testActivity.getClass(), new Object[] {connectionId}, workflowVersionChangeId);
    final MultiCloudTemporalActivityStubGeneratorFunction generatorFunction = spy(new MultiCloudTemporalActivityStubGeneratorFunction());
    doReturn(MultiCloudTemporalActivityStubGeneratorFunction.CURRENT_VERSION).when(generatorFunction).getWorkflowVersion(any());
    doReturn(testActivity).when(generatorFunction).generateActivityStub(any(), any());
    generatorFunction.setRouterService(routerService);

    final Object result = generatorFunction.apply(options);
    assertEquals(testActivity, result);
  }

}
