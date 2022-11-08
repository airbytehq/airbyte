/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.DbMigrationApiController;
import io.airbyte.server.apis.factories.DbMigrationApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class DbMigrationBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(DbMigrationApiFactory.class)
        .to(DbMigrationApiController.class)
        .in(RequestScoped.class);
  }

}
