/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.support;

import io.temporal.activity.ActivityOptions;

/**
 * Functional interface that defines the function used to generate a Temporal activity stub.
 *
 * @param <C> The Temporal activity stub class.
 * @param <A> The {@link ActivityOptions} for the Temporal activity stub.
 * @param <O> The Temporal activity stub object.
 */
@FunctionalInterface
public interface TemporalActivityStubGeneratorFunction<C extends Class<?>, A extends ActivityOptions, O> {

  O apply(C c, A a);

}
