/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.annotations;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Denotes a field in a Temporal workflow that represents a Temporal activity stub. Fields marked
 * with this annotation will automatically have a Temporal activity stub created, if not already
 * initialized when execution of the Temporal workflow starts.
 */
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.FIELD})
public @interface TemporalActivityStub {

  /**
   * The name of the singleton bean that holds the Temporal activity options for the Temporal activity
   * stub annotated by this annotation. This bean must exist in the application context.
   *
   * @return The name of the singleton bean that holds the Temporal activity options for that Temporal
   *         activity stub.
   */
  String activityOptionsBeanName();

}
