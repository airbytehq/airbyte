/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.functional;

import org.apache.commons.lang3.function.FailableConsumer;

@FunctionalInterface
public interface CheckedConsumer<T, E extends Throwable> extends FailableConsumer<T, E> {

}
