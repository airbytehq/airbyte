/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.config;

/**
 * Defines the different execution modes for the workers application.
 */
public final class WorkerMode {

  private WorkerMode() {}

  /**
   * Control plane environment/mode.
   */
  public static final String CONTROL_PLANE = "control-plane";

  /**
   * Data plane environment/mode.
   */
  public static final String DATA_PLANE = "data-plane";

}
