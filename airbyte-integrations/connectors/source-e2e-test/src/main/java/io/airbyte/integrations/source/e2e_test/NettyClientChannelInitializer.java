package io.airbyte.integrations.source.e2e_test;

import io.netty.channel.ChannelInitializer;
import io.netty.channel.socket.SocketChannel;
import io.netty.handler.codec.string.StringEncoder;

public class NettyClientChannelInitializer extends ChannelInitializer<SocketChannel> {

  @Override
  protected void initChannel(SocketChannel ch) {
    ch.pipeline().addLast(new StringEncoder());
  }

}
