/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.support;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.workers.temporal.annotations.TemporalActivityStub;
import io.micronaut.context.BeanRegistration;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import java.lang.reflect.Field;
import java.util.Collection;
import java.util.Optional;
import java.util.concurrent.Callable;
import lombok.extern.slf4j.Slf4j;
import net.bytebuddy.implementation.bind.annotation.RuntimeType;
import net.bytebuddy.implementation.bind.annotation.SuperCall;
import net.bytebuddy.implementation.bind.annotation.This;
import org.springframework.util.ReflectionUtils;

/**
 * Custom interceptor that handles invocations of Temporal workflow implementations to ensure that
 * any and all Temporal activity stubs are created prior to the first execution of the workflow.
 * This class is used in conjunction with {@link TemporalProxyHelper}. This approach is inspired by
 * https://github.com/applicaai/spring-boot-starter-temporal.
 *
 * @param <T> The type of the Temporal workflow.
 */
@Slf4j
public class TemporalActivityStubInterceptor<T> {

  /**
   * Function that generates Temporal activity stubs.
   *
   * Replace this value for unit testing.
   */
  private TemporalActivityStubGeneratorFunction<Class<?>, ActivityOptions, Object> activityStubGenerator = Workflow::newActivityStub;

  /**
   * The collection of configured {@link ActivityOptions} beans provided by the application framework.
   */
  private final Collection<BeanRegistration<ActivityOptions>> availableActivityOptions;

  /**
   * The type of the workflow implementation to be proxied.
   */
  private final Class<T> workflowImplClass;

  /**
   * Constructs a new interceptor for the provided workflow implementation class.
   *
   * @param workflowImplClass The Temporal workflow implementation class that will be intercepted.
   * @param availableActivityOptions The collection of configured {@link ActivityOptions} beans
   *        provided by the application framework.
   */
  public TemporalActivityStubInterceptor(final Class<T> workflowImplClass,
                                         final Collection<BeanRegistration<ActivityOptions>> availableActivityOptions) {
    this.workflowImplClass = workflowImplClass;
    this.availableActivityOptions = availableActivityOptions;
  }

  /**
   * Main interceptor method that will be invoked by the proxy.
   *
   * @param workflowImplInstance The actual workflow implementation object invoked on the proxy
   *        Temporal workflow instance.
   * @param call A {@link Callable} used to invoke the proxied method.
   * @return The result of the proxied method execution.
   * @throws Exception if the proxied method throws a checked exception
   * @throws IllegalStateException if the Temporal activity stubs associated with the workflow cannot
   *         be initialized.
   */
  @RuntimeType
  public Object execute(@This final T workflowImplInstance, @SuperCall final Callable<Object> call)
      throws Exception {
    // Initialize the activity stubs, if not already done, before execution of the workflow method
    initializeActivityStubs(workflowImplClass, workflowImplInstance);
    return call.call();
  }

  /**
   * Initializes all Temporal activity stubs present on the provided workflow instance. A Temporal
   * activity stub is denoted by the use of the {@link TemporalActivityStub} annotation on the field.
   *
   * @param workflowImplClass The target class of the proxy.
   * @param workflowInstance The workflow instance that may contain Temporal activity stub fields.
   */
  private void initializeActivityStubs(final Class<T> workflowImplClass,
                                       final T workflowInstance) {
    for (final Field field : workflowImplClass.getDeclaredFields()) {
      if (field.isAnnotationPresent(TemporalActivityStub.class)) {
        initializeActivityStub(workflowInstance, field);
      }
    }
  }

  /**
   * Initializes the Temporal activity stub represented by the provided field on the provided object,
   * if not already set.
   *
   * @param workflowInstance The Temporal workflow instance that contains the Temporal activity stub
   *        field.
   * @param activityStubField The field that represents the Temporal activity stub.
   */
  private void initializeActivityStub(final T workflowInstance,
                                      final Field activityStubField) {
    try {
      log.debug("Attempting to initialize Temporal activity stub for activity '{}' on workflow '{}'...", activityStubField.getType(),
          workflowInstance.getClass().getName());
      ReflectionUtils.makeAccessible(activityStubField);
      if (activityStubField.get(workflowInstance) == null) {
        final ActivityOptions activityOptions = getActivityOptions(activityStubField);
        final Object activityStub = generateActivityStub(activityStubField, activityOptions);
        activityStubField.set(workflowInstance, activityStub);
        log.debug("Initialized Temporal activity stub for activity '{}' for workflow '{}'.", activityStubField.getType(),
            workflowInstance.getClass().getName());
      } else {
        log.debug("Temporal activity stub '{}' is already initialized for Temporal workflow '{}'.",
            activityStubField.getType(),
            workflowInstance.getClass().getName());
      }
    } catch (final IllegalArgumentException | IllegalAccessException | IllegalStateException e) {
      log.error("Unable to initialize Temporal activity stub for activity '{}' for workflow '{}'.", activityStubField.getType(),
          workflowInstance.getClass().getName(), e);
      throw new RuntimeException(e);
    }
  }

  /**
   * Extracts the Temporal {@link ActivityOptions} from the {@link Field} on the provided target
   * instance object.
   *
   * @param activityStubField The field that represents the Temporal activity stub.
   * @return The Temporal {@link ActivityOptions} from the {@link Field} on the provided Temporal
   *         workflow instance object.
   * @throws IllegalStateException if the referenced Temporal {@link ActivityOptions} bean cannot be
   *         located.
   */
  private ActivityOptions getActivityOptions(final Field activityStubField) {
    final TemporalActivityStub annotation = activityStubField.getAnnotation(TemporalActivityStub.class);
    final String activityOptionsBeanName = annotation.activityOptionsBeanName();
    final Optional<ActivityOptions> selectedActivityOptions =
        availableActivityOptions.stream().filter(b -> b.getIdentifier().getName().equalsIgnoreCase(activityOptionsBeanName)).map(b -> b.getBean())
            .findFirst();
    if (selectedActivityOptions.isPresent()) {
      return selectedActivityOptions.get();
    } else {
      throw new IllegalStateException("No activity options bean of name '" + activityOptionsBeanName + "' exists.");
    }
  }

  /**
   * Retrieve the activity stub generator function associated with the Temporal activity stub.
   *
   * @param activityStubField The field that represents the Temporal activity stub.
   * @return The {@link TemporalActivityStubGeneratorFunction} associated with the Temporal activity
   *         stub.
   * @throws IllegalStateException if the referenced {@link TemporalActivityStubGeneratorFunction}
   *         bean cannot be located.
   */
  private Object generateActivityStub(final Field activityStubField, final ActivityOptions activityOptions) {
    return activityStubGenerator.apply(activityStubField.getType(), activityOptions);
  }

  @VisibleForTesting
  void setActivityStubGenerator(final TemporalActivityStubGeneratorFunction<Class<?>, ActivityOptions, Object> activityStubGenerator) {
    this.activityStubGenerator = activityStubGenerator;
  }

}
