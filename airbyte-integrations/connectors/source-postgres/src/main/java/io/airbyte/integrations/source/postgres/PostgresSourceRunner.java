/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import io.airbyte.integrations.base.adaptive.AdaptiveSourceRunner;

public class PostgresSourceRunner {

  public static void main(final String[] args) throws Exception {
    AdaptiveSourceRunner.baseOnEnv()
        .withOssSource(PostgresSource::sshWrappedSource)
        .withCloudSource(PostgresSourceStrictEncrypt::new)
        .run(args);
  }

}
