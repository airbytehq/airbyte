/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.lang

import java.util.*

interface CloseableQueue<E> : Queue<E>, AutoCloseable
