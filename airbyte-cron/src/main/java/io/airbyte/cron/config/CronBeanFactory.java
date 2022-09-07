/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cron.config;

import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Value;
import java.nio.file.Path;
import javax.inject.Named;
import javax.inject.Singleton;

@Factory
public class CronBeanFactory {

  @Singleton
  @Named("workspaceRootCron")
  public Path workspaceRoot(@Value("${airbyte.workspace.root}") final String workspaceRoot) {
    return Path.of(workspaceRoot);
  }

}
