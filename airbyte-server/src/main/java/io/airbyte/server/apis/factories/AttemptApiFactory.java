/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.server.apis.AttemptApiController;
import java.util.Map;
import org.glassfish.hk2.api.Factory;
import org.slf4j.MDC;

public class AttemptApiFactory implements Factory<AttemptApiController> {

  private static JobPersistence jobPersistence;
  private static Map<String, String> mdc;

  public static void setValues(final JobPersistence jobPersistence, final Map<String, String> mdc) {
    AttemptApiFactory.jobPersistence = jobPersistence;
    AttemptApiFactory.mdc = mdc;
  }

  @Override
  public AttemptApiController provide() {
    MDC.setContextMap(AttemptApiFactory.mdc);

    return new AttemptApiController(jobPersistence);
  }

  @Override
  public void dispose(final AttemptApiController instance) {
    /* no op */
  }

}
