/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.lang

import java.util.function.Consumer

interface CloseableConsumer<T> : Consumer<T>, AutoCloseable
