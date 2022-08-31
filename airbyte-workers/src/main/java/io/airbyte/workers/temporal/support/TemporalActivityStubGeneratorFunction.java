/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.support;

/**
 * Functional interface that defines the function used to generate a Temporal activity stub.
 *
 * @param <O> The Temporal activity stub object.
 */
@FunctionalInterface
public interface TemporalActivityStubGeneratorFunction<T extends TemporalActivityStubGenerationOptions, O> {

  O apply(TemporalActivityStubGenerationOptions t);

}
