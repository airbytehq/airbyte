/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.lang;

import java.util.function.Consumer;

public interface CloseableConsumer<T> extends Consumer<T>, AutoCloseable {}
