package io.dataline.server;

import io.dataline.server.apis.ConfigurationApi;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;
import org.glassfish.jersey.server.ResourceConfig;
import org.glassfish.jersey.servlet.ServletContainer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ServerApp {
  private static final Logger LOGGER = LoggerFactory.getLogger(ServerApp.class);

  public void start() throws Exception {
    Server server = new Server(8000);

    ServletContextHandler handler = new ServletContextHandler();

    ResourceConfig rc = new ResourceConfig().registerClasses(ConfigurationApi.class);

    ServletHolder configServlet = new ServletHolder(new ServletContainer(rc));

    handler.addServlet(configServlet, "/api/v1/*");

    server.setHandler(handler);

    server.start();
    server.join();
  }

  public static void main(String[] args) throws Exception {
    LOGGER.info("Starting server...");

    new ServerApp().start();
  }
}
