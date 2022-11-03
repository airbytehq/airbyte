/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.binders;

import io.airbyte.server.apis.NotificationsApiController;
import io.airbyte.server.apis.factories.NotificationsApiFactory;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.process.internal.RequestScoped;

public class NotificationApiBinder extends AbstractBinder {

  @Override
  protected void configure() {
    bindFactory(NotificationsApiFactory.class)
        .to(NotificationsApiController.class)
        .in(RequestScoped.class);
  }

}
