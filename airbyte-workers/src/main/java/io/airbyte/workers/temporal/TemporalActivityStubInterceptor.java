/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.workers.temporal.annotations.TemporalActivityStub;
import io.airbyte.workers.temporal.support.TemporalActivityStubGenerationOptions;
import io.airbyte.workers.temporal.support.TemporalActivityStubGeneratorFunction;
import io.micronaut.context.BeanRegistration;
import io.temporal.activity.ActivityOptions;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.util.Collection;
import java.util.Optional;
import java.util.concurrent.Callable;
import lombok.extern.slf4j.Slf4j;
import net.bytebuddy.implementation.bind.annotation.AllArguments;
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
   * The collection of configured {@link ActivityOptions} beans provided by the application framework.
   */
  private final Collection<BeanRegistration<ActivityOptions>> availableActivityOptions;

  /**
   * Collection of configured {@link TemporalActivityStubGeneratorFunction} beans provided by the
   * application framework.
   */
  private final Collection<BeanRegistration<TemporalActivityStubGeneratorFunction>> availableGeneratorFunctions;

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
   * @param availableGeneratorFunctions The collection of configured
   *        {@link TemporalActivityStubGeneratorFunction} beans provided by the application framework.
   */
  public TemporalActivityStubInterceptor(final Class<T> workflowImplClass,
                                         final Collection<BeanRegistration<ActivityOptions>> availableActivityOptions,
                                         final Collection<BeanRegistration<TemporalActivityStubGeneratorFunction>> availableGeneratorFunctions) {
    this.workflowImplClass = workflowImplClass;
    this.availableActivityOptions = availableActivityOptions;
    this.availableGeneratorFunctions = availableGeneratorFunctions;
  }

  /**
   * Main interceptor method that will be invoked by the proxy.
   *
   * @param workflowImplInstance The actual workflow implementation object invoked on the proxy
   *        Temporal workflow instance.
   * @param call A {@link Callable} used to invoke the proxied method.
   * @param args The arguments passed to the proxy invoked method.
   * @return The result of the proxied method execution.
   * @throws Exception if the proxied method throws a checked exception
   * @throws IllegalStateException if the Temporal activity stubs associated with the workflow cannot
   *         be initialized.
   */
  @RuntimeType
  public Object execute(@This final T workflowImplInstance, @SuperCall final Callable<Object> call, @AllArguments final Object[] args)
      throws Exception {
    // Initialize the activity stubs, if not already done, before execution of the workflow method
    initializeActivityStubs(workflowImplClass, workflowImplInstance, availableActivityOptions, args);
    return call.call();
  }

  /**
   * Initializes all Temporal activity stubs present on the provided workflow instance. A Temporal
   * activity stub is denoted by the use of the {@link TemporalActivityStub} annotation on the field.
   *
   * @param workflowImplClass The target class of the proxy.
   * @param workflowInstance The workflow instance that may contain Temporal activity stub fields.
   * @param activityOptions The collection of {@link ActivityOptions} beans configured in the
   *        application context.
   */
  private void initializeActivityStubs(final Class<T> workflowImplClass,
                                       final T workflowInstance,
                                       final Collection<BeanRegistration<ActivityOptions>> activityOptions,
                                       final Object[] methodArguments) {
    for (final Field field : workflowImplClass.getDeclaredFields()) {
      if (field.isAnnotationPresent(TemporalActivityStub.class)) {
        initializeActivityStub(workflowInstance, field, activityOptions, methodArguments);
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
   * @param activityOptions The collection of {@link ActivityOptions} beans configured in the
   *        application context.
   */
  private void initializeActivityStub(final T workflowInstance,
                                      final Field activityStubField,
                                      final Collection<BeanRegistration<ActivityOptions>> activityOptions,
                                      final Object[] methodArguments) {
    try {
      log.debug("Attempting to initialize Temporal activity stub for activity '{}' on workflow '{}'...", activityStubField.getType(),
          workflowInstance.getClass().getName());
      ReflectionUtils.makeAccessible(activityStubField);
      if (activityStubField.get(workflowInstance) == null) {
        final TemporalActivityStubGenerationOptions generationOptions = getGenerationOptions(activityStubField, methodArguments);
        final TemporalActivityStubGeneratorFunction generatorFunction = getGeneratorFunction(activityStubField);
        final Object activityStub = generatorFunction.apply(generationOptions);
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
  private TemporalActivityStubGeneratorFunction getGeneratorFunction(final Field activityStubField) {
    final TemporalActivityStub annotation = activityStubField.getAnnotation(TemporalActivityStub.class);
    final String generatorFunctionBeanName = annotation.activityGeneratorBeanName();
    final Optional<TemporalActivityStubGeneratorFunction> selectedGeneratorFunction =
        availableGeneratorFunctions.stream().filter(b -> b.getIdentifier().getName().equalsIgnoreCase(generatorFunctionBeanName))
            .map(b -> b.getBean()).findFirst();
    if (selectedGeneratorFunction.isPresent()) {
      return selectedGeneratorFunction.get();
    } else {
      throw new IllegalStateException("No activity generator function beans of name '" + generatorFunctionBeanName + "' exists.");
    }
  }

  /**
   * Builds the {@link TemporalActivityStubGenerationOptions} used to generate the Temporal activity
   * stub.
   *
   * @param activityStubField The field that represents the Temporal activity stub.
   * @param methodArguments The arguments passed to the proxy invoked method.
   * @return The {@link TemporalActivityStubGenerationOptions} to be used to generate a Temporal
   *         activity stub.
   */
  private TemporalActivityStubGenerationOptions getGenerationOptions(final Field activityStubField, final Object[] methodArguments) {
    final ActivityOptions activityOptions = getActivityOptions(activityStubField);
    final Class<?> activityStubClass = activityStubField.getType();
    final String workflowVersionChangedId = getWorkflowVersionChangeId(activityStubField);
    return new TemporalActivityStubGenerationOptions(activityOptions, activityStubClass, methodArguments, workflowVersionChangedId);
  }

  /**
   * Retrieves the Temporal workflow version change ID associated with the Temporal activity stub.
   *
   * @param activityStubField The field that represents the Temporal activity stub.
   * @return The configured Temporal workflow version change ID associated with the Temporal activity
   *         stub.
   */
  private String getWorkflowVersionChangeId(final Field activityStubField) {
    final TemporalActivityStub annotation = activityStubField.getAnnotation(TemporalActivityStub.class);
    return annotation.workflowVersionChangeId();
  }

  /**
   * Handle the given {@link InvocationTargetException}. Throws the underlying
   * {@link RuntimeException} or {@link Error} in case of such a root cause. Otherwise, the
   * {@link Exception} is thrown.
   *
   * @param e The {@link InvocationTargetException}.
   * @throws Exception the underlying cause exception extracted from the
   *         {@link InvocationTargetException}.
   */
  @VisibleForTesting
  static void handleInvocationTargetException(final InvocationTargetException e) throws Exception {
    if (e.getTargetException() instanceof Error) {
      throw (Error) e.getTargetException();
    } else if (e.getTargetException() instanceof RuntimeException) {
      throw (RuntimeException) e.getTargetException();
    } else {
      throw (Exception) e.getTargetException();
    }
  }

}
