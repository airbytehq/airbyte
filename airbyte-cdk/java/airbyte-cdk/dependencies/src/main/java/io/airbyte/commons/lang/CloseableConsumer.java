/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.lang;

import java.util.function.Consumer;

public interface CloseableConsumer<T> extends Consumer<T>, AutoCloseable {}
