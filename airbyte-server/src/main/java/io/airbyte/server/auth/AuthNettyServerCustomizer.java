/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.auth;

import io.micronaut.context.event.BeanCreatedEvent;
import io.micronaut.context.event.BeanCreatedEventListener;
import io.micronaut.http.server.netty.NettyServerCustomizer;
import io.micronaut.http.server.netty.NettyServerCustomizer.Registry;
import io.netty.channel.Channel;
import jakarta.inject.Singleton;

/**
 * Custom Netty customizer that registers the {@link AuthorizationServerHandler} with the Netty
 * stream pipeline. <br />
 * <br />
 * This customizer registers the handler as the first in the pipeline to ensure that it can read
 * and, if necessary, modify the incoming HTTP request to include a header that can be used to
 * determine authorization.
 */
@Singleton
public class AuthNettyServerCustomizer implements BeanCreatedEventListener<NettyServerCustomizer.Registry> {

  private final AuthorizationServerHandler authorizationServerHandler;

  public AuthNettyServerCustomizer(final AuthorizationServerHandler authorizationServerHandler) {
    this.authorizationServerHandler = authorizationServerHandler;
  }

  @Override
  public Registry onCreated(final BeanCreatedEvent<Registry> event) {
    final NettyServerCustomizer.Registry registry = event.getBean();
    registry.register(new Customizer(null)); //
    return registry;
  }

  private class Customizer implements NettyServerCustomizer {

    private final Channel channel;

    Customizer(final Channel channel) {
      this.channel = channel;
    }

    @Override
    public NettyServerCustomizer specializeForChannel(final Channel channel, final ChannelRole role) {
      return new Customizer(channel);
    }

    @Override
    public void onStreamPipelineBuilt() {
      channel.pipeline().addFirst(
          "authorizationHelper",
          authorizationServerHandler);
    }

  }

}
