/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.lang;

import java.util.Queue;

public interface CloseableQueue<E> extends Queue<E>, AutoCloseable {

}
