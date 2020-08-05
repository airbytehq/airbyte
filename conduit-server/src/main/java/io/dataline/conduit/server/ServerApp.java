package io.dataline.conduit.server;

import io.dataline.conduit.server.apis.PetApi;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;
import org.glassfish.jersey.server.ResourceConfig;
import org.glassfish.jersey.servlet.ServletContainer;

public class ServerApp {

    public ServerApp() {
    }

    public void start() throws Exception {
        Server server = new Server(8080);

        ServletContextHandler handler = new ServletContextHandler();

        ResourceConfig rc = new ResourceConfig()
                .registerClasses(PetApi.class);

        ServletHolder conduitServlet = new ServletHolder(new ServletContainer(rc));

        handler.addServlet(conduitServlet, "/api/v1/*");

        server.setHandler(handler);

        server.start();
        server.join();
    }

    public static void main(String[] args) throws Exception {
        System.out.println("Starting Server...");

        new ServerApp().start();
    }
}
