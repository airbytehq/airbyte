/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.functional;

import org.apache.commons.lang3.function.FailableBiConsumer;

@FunctionalInterface
public interface CheckedBiConsumer<T, R, E extends Throwable> extends FailableBiConsumer<T, R, E> {

}
