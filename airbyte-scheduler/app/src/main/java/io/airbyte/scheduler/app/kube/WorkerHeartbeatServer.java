package io.airbyte.scheduler.app.kube;

import com.google.common.collect.ImmutableMap;
import com.google.common.net.HttpHeaders;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteVersion;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Map;

public class WorkerHeartbeatServer {

    private final int port;

    public WorkerHeartbeatServer(int port) {
        this.port = port;
    }

    public void start() throws Exception {
        final Server server = getServer();
        server.start();
        server.join();
    }

    protected Server getServer() {
        Server server = new Server(port);
        ServletContextHandler handler = new ServletContextHandler();
        handler.addServlet(WorkerHeartbeatServlet.class, "/*");
        server.setHandler(handler);

        return server;
    }

    public static class WorkerHeartbeatServlet extends HttpServlet {

        public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
            this.serveDefaultRequest(response);
        }

        public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
            this.serveDefaultRequest(response);
        }

        public void doOptions(HttpServletRequest request, HttpServletResponse response) throws IOException {
            this.addCorsHeaders(response);
        }

        private void serveDefaultRequest(HttpServletResponse response) throws IOException {
            var outputMap = ImmutableMap.of("up", true);

            this.addCorsHeaders(response);

            response.setContentType("application/json");
            response.setStatus(HttpServletResponse.SC_OK);
            response.getWriter().println(Jsons.serialize(outputMap));
        }

        private void addCorsHeaders(HttpServletResponse response) {
            for (Map.Entry<String, String> entry : CORS_FILTER_MAP.entrySet()) {
                response.setHeader(entry.getKey(), entry.getValue());
            }
        }

    }

    private static final ImmutableMap<String, String> CORS_FILTER_MAP = ImmutableMap.of(
            HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN, "*",
            HttpHeaders.ACCESS_CONTROL_ALLOW_HEADERS, "Origin, Content-Type, Accept, Content-Encoding",
            HttpHeaders.ACCESS_CONTROL_ALLOW_METHODS, "GET, POST, PUT, DELETE, OPTIONS, HEAD");

}
