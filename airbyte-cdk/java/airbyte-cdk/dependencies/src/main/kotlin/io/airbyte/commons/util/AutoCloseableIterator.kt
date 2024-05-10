/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.util

/**
 * If you operate on this iterator, you better close it. [AutoCloseableIterator.close] must be
 * idempotent. The contract on this interface is that it may be called MANY times.
 *
 * @param <T> type </T>
 */
interface AutoCloseableIterator<T> : MutableIterator<T>, AutoCloseable, AirbyteStreamAware
