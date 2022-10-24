/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.server.apis.AttemptApiImpl;
import java.util.Map;
import org.glassfish.hk2.api.Factory;
import org.slf4j.MDC;

public class AttemptApiFactory implements Factory<AttemptApiImpl> {

  private static JobPersistence jobPersistence;
  private static Map<String, String> mdc;

  public static void setValues(final JobPersistence jobPersistence, final Map<String, String> mdc) {
    AttemptApiFactory.jobPersistence = jobPersistence;
    AttemptApiFactory.mdc = mdc;
  }

  @Override
  public AttemptApiImpl provide() {
    MDC.setContextMap(AttemptApiFactory.mdc);

    return new AttemptApiImpl(jobPersistence);
  }

  @Override
  public void dispose(final AttemptApiImpl instance) {
    /* no op */
  }

}
