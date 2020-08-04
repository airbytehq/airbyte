package io.dataline.conduit.server;

import org.eclipse.jetty.server.Connector;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.ServerConnector;

public class ServerApp {


    public ServerApp() {
    }

    public void start() {
        Server server = new Server();
        ServerConnector connector = new ServerConnector(server);
        connector.setPort(8090);
        server.setConnectors(new Connector[] {connector});
    }

    public static void main(String[] args) {
        System.out.println("Starting Server...");

        new ServerApp().start();
    }
}
