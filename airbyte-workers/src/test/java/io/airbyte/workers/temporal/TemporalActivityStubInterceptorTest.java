/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.workers.temporal.exception.RetryableException;
import io.airbyte.workers.temporal.stubs.ErrorTestWorkflowImpl;
import io.airbyte.workers.temporal.stubs.InvalidTestWorkflowImpl;
import io.airbyte.workers.temporal.stubs.TestActivity;
import io.airbyte.workers.temporal.stubs.ValidTestWorkflowImpl;
import io.airbyte.workers.temporal.support.TemporalActivityStubGenerationOptions;
import io.airbyte.workers.temporal.support.TemporalActivityStubGeneratorFunction;
import io.micronaut.context.BeanRegistration;
import io.micronaut.inject.BeanIdentifier;
import io.temporal.activity.ActivityOptions;
import java.lang.reflect.InvocationTargetException;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.invocation.InvocationOnMock;
import org.mockito.stubbing.Answer;

/**
 * Test suite for the {@link TemporalActivityStubInterceptor} class.
 */
class TemporalActivityStubInterceptorTest {

  private static final String ACTIVITY_OPTIONS = "activityOptions";

  @Test
  void testExecutionOfValidWorkflowWithActivities() throws Exception {
    final ActivityOptions activityOptions = mock(ActivityOptions.class);
    final TemporalActivityStubGeneratorFunction generatorFunction = (TemporalActivityStubGenerationOptions o) -> mock(o.getActivityStubClass());

    final BeanIdentifier activityOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration activityOptionsBeanRegistration = mock(BeanRegistration.class);
    when(activityOptionsBeanIdentifier.getName()).thenReturn(ACTIVITY_OPTIONS);
    when(activityOptionsBeanRegistration.getIdentifier()).thenReturn(activityOptionsBeanIdentifier);
    when(activityOptionsBeanRegistration.getBean()).thenReturn(activityOptions);

    final BeanIdentifier generatorFunctionOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration generatorFunctionBeanRegistration = mock(BeanRegistration.class);
    when(generatorFunctionOptionsBeanIdentifier.getName()).thenReturn("defaultTemporalActivityStubGeneratorFunction");
    when(generatorFunctionBeanRegistration.getIdentifier()).thenReturn(generatorFunctionOptionsBeanIdentifier);
    when(generatorFunctionBeanRegistration.getBean()).thenReturn(generatorFunction);

    final TemporalActivityStubInterceptor interceptor = new TemporalActivityStubInterceptor(ValidTestWorkflowImpl.class,
        List.of(activityOptionsBeanRegistration), List.of(generatorFunctionBeanRegistration));

    final ValidTestWorkflowImpl validTestWorklowImpl = new ValidTestWorkflowImpl();
    final Callable<Void> callable = () -> {
      validTestWorklowImpl.run();
      return null;
    };

    interceptor.execute(validTestWorklowImpl, callable, null);
    Assertions.assertTrue(validTestWorklowImpl.isHasRun());
  }

  @Test
  void testExecutionOfValidWorkflowWithActivitiesThatThrows() throws Exception {
    final ActivityOptions activityOptions = mock(ActivityOptions.class);
    final TemporalActivityStubGeneratorFunction generatorFunction = (TemporalActivityStubGenerationOptions o) -> mock(o.getActivityStubClass());

    final BeanIdentifier activityOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration activityOptionsBeanRegistration = mock(BeanRegistration.class);
    when(activityOptionsBeanIdentifier.getName()).thenReturn(ACTIVITY_OPTIONS);
    when(activityOptionsBeanRegistration.getIdentifier()).thenReturn(activityOptionsBeanIdentifier);
    when(activityOptionsBeanRegistration.getBean()).thenReturn(activityOptions);

    final BeanIdentifier generatorFunctionOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration generatorFunctionBeanRegistration = mock(BeanRegistration.class);
    when(generatorFunctionOptionsBeanIdentifier.getName()).thenReturn("defaultTemporalActivityStubGeneratorFunction");
    when(generatorFunctionBeanRegistration.getIdentifier()).thenReturn(generatorFunctionOptionsBeanIdentifier);
    when(generatorFunctionBeanRegistration.getBean()).thenReturn(generatorFunction);

    final TemporalActivityStubInterceptor interceptor = new TemporalActivityStubInterceptor(ErrorTestWorkflowImpl.class,
        List.of(activityOptionsBeanRegistration), List.of(generatorFunctionBeanRegistration));

    final ErrorTestWorkflowImpl errorTestWorkflowImpl = new ErrorTestWorkflowImpl();
    final Callable<Void> callable = () -> {
      errorTestWorkflowImpl.run();
      return null;
    };

    Assertions.assertThrows(RetryableException.class, () -> {
      interceptor.execute(errorTestWorkflowImpl, callable, null);
    });
  }

  @Test
  void testActivityStubsAreOnlyInitializedOnce() throws Exception {
    final AtomicInteger activityStubInitializationCounter = new AtomicInteger(0);
    final ActivityOptions activityOptions = mock(ActivityOptions.class);
    final TestActivity testActivity = mock(TestActivity.class);
    final TemporalActivityStubGeneratorFunction generatorFunction = mock(TemporalActivityStubGeneratorFunction.class);
    when(generatorFunction.apply(any())).thenAnswer(new Answer<Object>() {
      @Override
      public Object answer(final InvocationOnMock invocation) throws Throwable {
        activityStubInitializationCounter.incrementAndGet();
        return testActivity;
      }
    });

    final BeanIdentifier activityOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration activityOptionsBeanRegistration = mock(BeanRegistration.class);
    when(activityOptionsBeanIdentifier.getName()).thenReturn(ACTIVITY_OPTIONS);
    when(activityOptionsBeanRegistration.getIdentifier()).thenReturn(activityOptionsBeanIdentifier);
    when(activityOptionsBeanRegistration.getBean()).thenReturn(activityOptions);

    final BeanIdentifier generatorFunctionOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration generatorFunctionBeanRegistration = mock(BeanRegistration.class);
    when(generatorFunctionOptionsBeanIdentifier.getName()).thenReturn("defaultTemporalActivityStubGeneratorFunction");
    when(generatorFunctionBeanRegistration.getIdentifier()).thenReturn(generatorFunctionOptionsBeanIdentifier);
    when(generatorFunctionBeanRegistration.getBean()).thenReturn(generatorFunction);

    final TemporalActivityStubInterceptor interceptor = new TemporalActivityStubInterceptor(ValidTestWorkflowImpl.class,
        List.of(activityOptionsBeanRegistration), List.of(generatorFunctionBeanRegistration));

    final ValidTestWorkflowImpl validTestWorklowImpl = new ValidTestWorkflowImpl();
    final Callable<Void> callable = () -> {
      validTestWorklowImpl.run();
      return null;
    };
    interceptor.execute(validTestWorklowImpl, callable, null);
    interceptor.execute(validTestWorklowImpl, callable, null);
    interceptor.execute(validTestWorklowImpl, callable, null);
    interceptor.execute(validTestWorklowImpl, callable, null);

    Assertions.assertEquals(1, activityStubInitializationCounter.get());
  }

  @Test
  void testExecutionOfInvalidWorkflowWithActivityWithMissingActivityOptions() throws Exception {
    final ActivityOptions activityOptions = mock(ActivityOptions.class);
    final TestActivity testActivity = mock(TestActivity.class);
    final TemporalActivityStubGeneratorFunction generatorFunction = (TemporalActivityStubGenerationOptions o) -> testActivity;

    final BeanIdentifier activityOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration activityOptionsBeanRegistration = mock(BeanRegistration.class);
    when(activityOptionsBeanIdentifier.getName()).thenReturn(ACTIVITY_OPTIONS);
    when(activityOptionsBeanRegistration.getIdentifier()).thenReturn(activityOptionsBeanIdentifier);
    when(activityOptionsBeanRegistration.getBean()).thenReturn(activityOptions);

    final BeanIdentifier generatorFunctionOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration generatorFunctionBeanRegistration = mock(BeanRegistration.class);
    when(generatorFunctionOptionsBeanIdentifier.getName()).thenReturn("defaultTemporalActivityStubGeneratorFunction");
    when(generatorFunctionBeanRegistration.getIdentifier()).thenReturn(generatorFunctionOptionsBeanIdentifier);
    when(generatorFunctionBeanRegistration.getBean()).thenReturn(generatorFunction);

    final TemporalActivityStubInterceptor interceptor = new TemporalActivityStubInterceptor(InvalidTestWorkflowImpl.class,
        List.of(activityOptionsBeanRegistration), List.of(generatorFunctionBeanRegistration));

    final InvalidTestWorkflowImpl invalidTestWorklowImpl = new InvalidTestWorkflowImpl();
    final Callable<Void> callable = () -> {
      invalidTestWorklowImpl.run();
      return null;
    };

    final RuntimeException exception = Assertions.assertThrows(RuntimeException.class, () -> {
      interceptor.execute(invalidTestWorklowImpl, callable, null);
    });
    Assertions.assertEquals(IllegalStateException.class, exception.getCause().getClass());
  }

  @Test
  void testInvocationTargetExceptionWithError() {
    final Error target = new IllegalAccessError();
    final InvocationTargetException e = new InvocationTargetException(target);
    Assertions.assertThrows(IllegalAccessError.class, () -> {
      TemporalActivityStubInterceptor.handleInvocationTargetException(e);
    });
  }

  @Test
  void testInvocationTargetExceptionWithRuntimeException() {
    final RuntimeException target = new NullPointerException();
    final InvocationTargetException e = new InvocationTargetException(target);
    Assertions.assertThrows(NullPointerException.class, () -> {
      TemporalActivityStubInterceptor.handleInvocationTargetException(e);
    });
  }

  @Test
  void testInvocationTargetExceptionWithCheckedException() {
    final Exception target = new RetryableException(new NullPointerException("test"));
    final InvocationTargetException e = new InvocationTargetException(target);
    Assertions.assertThrows(RetryableException.class, () -> {
      TemporalActivityStubInterceptor.handleInvocationTargetException(e);
    });
  }

}
