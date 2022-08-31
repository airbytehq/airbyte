/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import static org.junit.Assert.assertNotNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.workers.temporal.stubs.ValidTestWorkflowImpl;
import io.airbyte.workers.temporal.support.TemporalActivityStubGenerationOptions;
import io.airbyte.workers.temporal.support.TemporalActivityStubGeneratorFunction;
import io.micronaut.context.BeanRegistration;
import io.micronaut.inject.BeanIdentifier;
import io.temporal.activity.ActivityOptions;
import io.temporal.common.RetryOptions;
import java.lang.reflect.InvocationTargetException;
import java.time.Duration;
import java.util.List;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link TemporalProxyHelper} class.
 */
class TemporalProxyHelperTest {

  @Test
  void testProxyToImplementation() throws NoSuchMethodException, InvocationTargetException, InstantiationException, IllegalAccessException {
    final ActivityOptions activityOptions = ActivityOptions.newBuilder()
        .setHeartbeatTimeout(Duration.ofSeconds(30))
        .setStartToCloseTimeout(Duration.ofSeconds(120))
        .setRetryOptions(RetryOptions.newBuilder()
            .setMaximumAttempts(5)
            .setInitialInterval(Duration.ofSeconds(30))
            .setMaximumInterval(Duration.ofSeconds(600))
            .build())
        .build();

    final BeanIdentifier activityOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration activityOptionsBeanRegistration = mock(BeanRegistration.class);
    when(activityOptionsBeanIdentifier.getName()).thenReturn("activityOptions");
    when(activityOptionsBeanRegistration.getIdentifier()).thenReturn(activityOptionsBeanIdentifier);
    when(activityOptionsBeanRegistration.getBean()).thenReturn(activityOptions);

    final TemporalActivityStubGeneratorFunction generatorFunction = (TemporalActivityStubGenerationOptions o) -> mock(o.getActivityStubClass());
    final BeanIdentifier generatorFunctionOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration generatorFunctionBeanRegistration = mock(BeanRegistration.class);
    when(generatorFunctionOptionsBeanIdentifier.getName()).thenReturn("defaultTemporalActivityStubGeneratorFunction");
    when(generatorFunctionBeanRegistration.getIdentifier()).thenReturn(generatorFunctionOptionsBeanIdentifier);
    when(generatorFunctionBeanRegistration.getBean()).thenReturn(generatorFunction);

    final TemporalProxyHelper temporalProxyHelper =
        new TemporalProxyHelper(List.of(activityOptionsBeanRegistration), List.of(generatorFunctionBeanRegistration));

    final Class<ValidTestWorkflowImpl> proxy = temporalProxyHelper.proxyWorkflowClass(ValidTestWorkflowImpl.class);

    assertNotNull(proxy);

    final ValidTestWorkflowImpl proxyImplementation = proxy.getDeclaredConstructor().newInstance();
    proxyImplementation.run();
    Assertions.assertTrue(proxyImplementation.isHasRun());
  }

}
