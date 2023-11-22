package io.airbyte.cdk.integrations.base;

import io.netty.bootstrap.ServerBootstrap;
import io.netty.buffer.ByteBuf;
import io.netty.buffer.ByteBufInputStream;
import io.netty.channel.ChannelFuture;
import io.netty.channel.ChannelHandler.Sharable;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.ChannelInboundHandlerAdapter;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.ChannelOption;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.SocketChannel;
import io.netty.channel.socket.nio.NioServerSocketChannel;
import io.netty.util.ReferenceCountUtil;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.function.Consumer;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class DestinationListener {

  @Sharable
  public static class DestinationListenerHandler extends ChannelInboundHandlerAdapter { // (1)

    private Consumer<InputStream> inputStreamConsumer;

    private SerializedAirbyteMessageConsumer consumer;

    private ByteBuf tmp;
    public DestinationListenerHandler(Consumer<InputStream> inputStreamConsumer, SerializedAirbyteMessageConsumer consumer) {
      super();
      this.inputStreamConsumer = inputStreamConsumer;
      this.consumer = consumer;
    }

    @Override
    public void handlerAdded(ChannelHandlerContext ctx) {
      log.info("Handler added");
      try {
        consumer.start();
      } catch (Exception e) {
        log.error("Failed to start consumer", e);
      }
      tmp = ctx.alloc().buffer(4);
    }

    @Override
    public void handlerRemoved(ChannelHandlerContext ctx) {
      log.info("Handler removed");
      tmp.release();
      tmp = null;
      try {
        consumer.close();
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
    }

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) { // (2)
      ByteBuf in = (ByteBuf) msg;
      tmp.writeBytes(in);
      in.release();
      try {
        log.info("Consuming write stream");
        inputStreamConsumer.accept(new ByteBufInputStream(tmp));
      } catch (Exception e) {
        log.error("Failed to consume write stream", e);
      }
    }

    static void consumeWriteStream(final InputStream bis)
        throws Exception {
      final ByteArrayOutputStream baos = new ByteArrayOutputStream();

      final byte[] buffer = new byte[8192]; // 8K buffer
      int bytesRead;
      boolean lastWasNewLine = false;

      while ((bytesRead = bis.read(buffer)) != -1) {
        for (int i = 0; i < bytesRead; i++) {
          final byte b = buffer[i];
          if (b == '\n' || b == '\r') {
            if (!lastWasNewLine && baos.size() > 0) {
              System.out.println("Message: " + baos.toString(StandardCharsets.UTF_8) +" Size: " +baos.size());
              baos.reset();
            }
            lastWasNewLine = true;
          } else {
            baos.write(b);
            lastWasNewLine = false;
          }
        }
      }

      // Handle last line if there's one
      if (baos.size() > 0) {
        System.out.println("Message: " + baos.toString(StandardCharsets.UTF_8) +" Size: " +baos.size());
      }
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) { // (4)
      // Close the connection when an exception is raised.
      log.error("Exception caught", cause);
      cause.printStackTrace();
      ctx.close();
    }
  }

  private int port;

  private DestinationListenerHandler handler;

  private volatile ChannelFuture channel;
  private volatile EventLoopGroup parentGroup;
  private volatile EventLoopGroup workerGroup;

  public DestinationListener(int port, final DestinationListenerHandler handler) {
    this.port = port;
    this.handler = handler;
  }

  public void run() throws Exception {
    parentGroup = new NioEventLoopGroup(); // (1)
    workerGroup = new NioEventLoopGroup();
    try {
      log.info("Starting destination listener on port {}", port);
      ServerBootstrap b = new ServerBootstrap(); // (2)
      b.group(parentGroup, workerGroup)
          .channel(NioServerSocketChannel.class) // (3)
          .childHandler(new ChannelInitializer<SocketChannel>() { // (4)
            @Override
            public void initChannel(SocketChannel ch) throws Exception {
              ch.pipeline().addLast(handler);
            }
          })
          .option(ChannelOption.SO_BACKLOG, 128)          // (5)
          .childOption(ChannelOption.SO_KEEPALIVE, true); // (6)

      // Bind and start to accept incoming connections.
      channel = b.bind(port).sync(); // (7)

      channel.channel().closeFuture().sync();
      log.info("Destination channel closing", port);
    } finally {

    }
  }

  public void stop() throws Exception {
    log.info("Stopping netty eventloop groups");
    workerGroup.shutdownGracefully().sync();
    parentGroup.shutdownGracefully().sync();
  }

  public static void main(String[] args) throws Exception {
    int port = 8080;
    if (args.length > 0) {
      port = Integer.parseInt(args[0]);
    }

//    new DestinationListener(port, new DestinationListenerHandler(inputStream -> System.out.println(inputStream))).run();
  }
}
