/*
 * MIT License
 * 
 * Copyright (c) 2020 Dataline
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.dataline.server;

import io.dataline.server.apis.ConfigurationApi;
import io.dataline.server.errors.InvalidInputExceptionMapper;
import io.dataline.server.errors.InvalidJsonExceptionMapper;
import io.dataline.server.errors.KnownExceptionMapper;
import io.dataline.server.errors.UncaughtExceptionMapper;
import java.util.logging.Level;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.jackson.internal.jackson.jaxrs.json.JacksonJaxbJsonProvider;
import org.glassfish.jersey.logging.LoggingFeature;
import org.glassfish.jersey.process.internal.RequestScoped;
import org.glassfish.jersey.server.ResourceConfig;
import org.glassfish.jersey.servlet.ServletContainer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ServerApp {
  private static final Logger LOGGER = LoggerFactory.getLogger(ServerApp.class);
  private final String dbRoot;

  public ServerApp(String dbRoot) {

    this.dbRoot = dbRoot;
  }

  public void start() throws Exception {
    //    BasicDataSource connectionPool = DatabaseHelper.getConnectionPoolFromEnv();
    //    System.out.println("server-uuid = " + ServerUuid.get(connectionPool));

    Server server = new Server(8000);

    ServletContextHandler handler = new ServletContextHandler();

    ConfigurationApiFactory.setDbRoot(dbRoot);

    ResourceConfig rc =
        new ResourceConfig()
            // api
            .register(ConfigurationApi.class)
            .register(
                new AbstractBinder() {
                  @Override
                  public void configure() {
                    bindFactory(ConfigurationApiFactory.class)
                        .to(ConfigurationApi.class)
                        .in(RequestScoped.class);
                  }
                })
            // exception handling
            .register(InvalidJsonExceptionMapper.class)
            .register(InvalidInputExceptionMapper.class)
            .register(KnownExceptionMapper.class)
            .register(UncaughtExceptionMapper.class)
            // needed so that the custom json exception mappers don't get overridden
            // https://stackoverflow.com/questions/35669774/jersey-custom-exception-mapper-for-invalid-json-string
            .register(JacksonJaxbJsonProvider.class)
            // request logger
            // https://www.javaguides.net/2018/06/jersey-rest-logging-using-loggingfeature.html
            .register(
                new LoggingFeature(
                    java.util.logging.Logger.getLogger(LoggingFeature.DEFAULT_LOGGER_NAME),
                    Level.INFO,
                    LoggingFeature.Verbosity.PAYLOAD_ANY,
                    10000));

    ServletHolder configServlet = new ServletHolder(new ServletContainer(rc));

    handler.addServlet(configServlet, "/api/*");

    server.setHandler(handler);

    server.start();
    server.join();
  }

  public static void main(String[] args) throws Exception {
    LOGGER.info("Starting server...");

    new ServerApp("/Users/charles/code/dataline/data/config").start();
  }
}
