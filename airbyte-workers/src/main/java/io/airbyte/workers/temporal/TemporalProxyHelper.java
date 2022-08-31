/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import io.airbyte.workers.temporal.support.TemporalActivityStubGeneratorFunction;
import io.micronaut.context.BeanRegistration;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.QueryMethod;
import io.temporal.workflow.SignalMethod;
import io.temporal.workflow.WorkflowMethod;
import java.lang.annotation.Annotation;
import java.lang.reflect.Method;
import java.util.Collection;
import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;
import javax.inject.Inject;
import javax.inject.Singleton;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.bytebuddy.ByteBuddy;
import net.bytebuddy.TypeCache;
import net.bytebuddy.dynamic.loading.ClassLoadingStrategy;
import net.bytebuddy.implementation.MethodDelegation;
import net.bytebuddy.matcher.ElementMatchers;
import org.springframework.core.MethodIntrospector;
import org.springframework.core.annotation.AnnotationUtils;
import org.springframework.util.ReflectionUtils;

/**
 * Generates proxy classes which can be registered with Temporal. These proxies delegate all methods
 * to the provided bean/singleton to allow for the dependency injection framework to manage the
 * lifecycle of a Temporal workflow implementation. This approach is inspired by
 * https://github.com/applicaai/spring-boot-starter-temporal.
 */
@Singleton
@NoArgsConstructor
@Slf4j
public class TemporalProxyHelper {

  /**
   * Cache of already generated proxies to reduce the cost of creating and loading the proxies.
   */
  private static final TypeCache<Class<?>> WORKFLOW_PROXY_CACHE = new TypeCache<>();

  /**
   * Collection of available {@link ActivityOptions} beans which will be used to initialize Temporal
   * activity stubs in each registered Temporal workflow.
   */
  @Inject
  private Collection<BeanRegistration<ActivityOptions>> availableActivityOptions;

  /**
   * Collection of available {@link TemporalActivityStubGeneratorFunction} beans which will be used to
   * initialize Temporal activity stubs in each registered Temporal workflow.
   */
  @Inject
  private Collection<BeanRegistration<TemporalActivityStubGeneratorFunction>> availableGeneratorFunctions;

  public TemporalProxyHelper(final Collection<BeanRegistration<ActivityOptions>> availableActivityOptions,
                             final Collection<BeanRegistration<TemporalActivityStubGeneratorFunction>> availableGeneratorFunctions) {
    this.availableActivityOptions = availableActivityOptions;
    this.availableGeneratorFunctions = availableGeneratorFunctions;
  }

  /**
   * Creates a proxy class for the given workflow class implementation and instance.
   *
   * @param workflowImplClass The workflow implementation class to proxy. proxy.
   * @return A proxied workflow implementation class that can be registered with Temporal.
   * @param <T> The type of the workflow implementation class.
   */
  @SuppressWarnings("PMD.UnnecessaryCast")
  public <T> Class<T> proxyWorkflowClass(final Class<T> workflowImplClass) {
    log.debug("Creating a Temporal proxy for worker class '{}' with interface '{}'...", workflowImplClass.getName(),
        workflowImplClass.getInterfaces()[0]);
    return (Class<T>) WORKFLOW_PROXY_CACHE.findOrInsert(workflowImplClass.getClassLoader(), workflowImplClass, () -> {
      final Set<Method> workflowMethods = findAnnotatedMethods(workflowImplClass, WorkflowMethod.class);
      final Set<Method> signalMethods = findAnnotatedMethods(workflowImplClass, SignalMethod.class);
      final Set<Method> queryMethods = findAnnotatedMethods(workflowImplClass, QueryMethod.class);

      final Set<Method> proxiedMethods = new HashSet<>();
      proxiedMethods.add((Method) workflowMethods.toArray()[0]);
      proxiedMethods.addAll(signalMethods.stream().collect(Collectors.toList()));
      proxiedMethods.addAll(queryMethods.stream().collect(Collectors.toList()));

      final Class<T> type = (Class<T>) new ByteBuddy()
          .subclass(workflowImplClass)
          .name(workflowImplClass.getSimpleName() + "Proxy")
          .implement(workflowImplClass.getInterfaces()[0])
          .method(ElementMatchers.anyOf(proxiedMethods.toArray(new Method[] {})))
          .intercept(
              MethodDelegation.to(generateInterceptor(workflowImplClass, availableActivityOptions, availableGeneratorFunctions)))
          .make()
          .load(workflowImplClass.getClassLoader(), ClassLoadingStrategy.Default.WRAPPER)
          .getLoaded();

      log.debug("Temporal workflow proxy '{}' created for worker class '{}' with interface '{}'.", type.getName(), workflowImplClass.getName(),
          workflowImplClass.getInterfaces()[0]);
      return type;
    });
  }

  /**
   * Finds the methods annotated with the provided annotation type in the given class.
   *
   * @param workflowImplClass The workflow implementation class.
   * @param annotationClass The annotation.
   * @return The set of methods annotated with the provided annotation.
   * @param <A> The type of the annotation.
   */
  private <A extends Annotation> Set<Method> findAnnotatedMethods(final Class<?> workflowImplClass, final Class<A> annotationClass) {
    return MethodIntrospector.selectMethods(
        workflowImplClass,
        (ReflectionUtils.MethodFilter) method -> AnnotationUtils.findAnnotation(method, annotationClass) != null);
  }

  /**
   * Generates a {@link TemporalActivityStubInterceptor} instance for use with the generated proxy
   * workflow implementation.
   *
   * @param workflowImplClass The workflow implementation class.
   * @param availableActivityOptions The collection of available {@link ActivityOptions} beans which
   *        will be used to initialize Temporal activity stubs in each registered Temporal workflow.
   * @param availableGeneratorFunctions The collection of available
   *        {@link TemporalActivityStubGeneratorFunction} beans that will be used by the interceptor
   *        to generate Temporal activity stubs.
   * @return The generated {@link TemporalActivityStubInterceptor} instance.
   * @param <T> The workflow implementation type.
   */
  private <T> TemporalActivityStubInterceptor<T> generateInterceptor(final Class<T> workflowImplClass,
                                                                     final Collection<BeanRegistration<ActivityOptions>> availableActivityOptions,
                                                                     final Collection<BeanRegistration<TemporalActivityStubGeneratorFunction>> availableGeneratorFunctions) {
    return new TemporalActivityStubInterceptor(workflowImplClass, availableActivityOptions, availableGeneratorFunctions);
  }

}
