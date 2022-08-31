/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.support;

import io.temporal.workflow.Workflow;
import javax.inject.Named;
import javax.inject.Singleton;

@Singleton
@Named("defaultTemporalActivityStubGeneratorFunction")
public class DefaultTemporalActivityStubGeneratorFunction implements TemporalActivityStubGeneratorFunction {

  @Override
  public Object apply(final TemporalActivityStubGenerationOptions options) {
    return Workflow.newActivityStub(options.getActivityStubClass(), options.getActivityOptions());
  }

}
