/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import io.airbyte.db.instance.configs.jooq.enums.ReleaseStage;

/**
 * Keep track of all metric tags.
 */
public class MetricTags {

  private static final String RELEASE_STAGE = "release_stage:";

  public static String getReleaseStage(final ReleaseStage stage) {
    return RELEASE_STAGE + ":" + stage.getLiteral();
  }

}
