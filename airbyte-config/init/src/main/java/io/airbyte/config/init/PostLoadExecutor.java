/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

/**
 * Defines any additional tasks that should be executed after successful boostrapping of the Airbyte
 * environment.
 */
public interface PostLoadExecutor {

  /**
   * Executes the additional post bootstrapping tasks.
   *
   * @throws Exception if unable to perform the additional tasks.
   */
  void execute() throws Exception;

}
