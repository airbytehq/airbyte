package io.dataline.server;

import io.dataline.db.DatabaseHelper;
import io.dataline.server.apis.ConfigurationApi;
import io.dataline.server.errors.CatchAllExceptionMapper;
import io.dataline.server.errors.InvalidInputExceptionMapper;
import io.dataline.server.errors.InvalidJsonExceptionMapper;
import io.dataline.server.errors.KnownExceptionMapper;
import java.util.logging.Level;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;
import org.glassfish.jersey.jackson.internal.jackson.jaxrs.json.JacksonJaxbJsonProvider;
import org.glassfish.jersey.logging.LoggingFeature;
import org.glassfish.jersey.server.ResourceConfig;
import org.glassfish.jersey.servlet.ServletContainer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ServerApp {
  private static final Logger LOGGER = LoggerFactory.getLogger(ServerApp.class);

  public void start() throws Exception {
    DatabaseHelper.initializeDatabase();
    Server server = new Server(8000);

    ServletContextHandler handler = new ServletContextHandler();

    ResourceConfig rc =
        new ResourceConfig()
            // api
            .registerClasses(ConfigurationApi.class)
            // exception handling
            .register(InvalidJsonExceptionMapper.class)
            .register(InvalidInputExceptionMapper.class)
            .register(KnownExceptionMapper.class)
            .register(CatchAllExceptionMapper.class)
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

    new ServerApp().start();
  }
}
