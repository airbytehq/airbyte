/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import java.util.Optional;
import java.util.function.Consumer;

public interface FetchSizeEstimator extends Consumer<Object> {

  /**
   * @return the estimated fetch size when the estimation is ready
   */
  Optional<Integer> getFetchSize();

}
