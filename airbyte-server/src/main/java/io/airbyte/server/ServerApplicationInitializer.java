package io.airbyte.server;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.server.errors.InvalidInputExceptionMapper;
import io.airbyte.server.errors.InvalidJsonExceptionMapper;
import io.airbyte.server.errors.InvalidJsonInputExceptionMapper;
import io.airbyte.server.errors.KnownExceptionMapper;
import io.airbyte.server.errors.NotFoundExceptionMapper;
import io.airbyte.server.errors.UncaughtExceptionMapper;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.env.Environment;
import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.discovery.event.ServiceReadyEvent;
import jakarta.inject.Singleton;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;
import org.glassfish.jersey.jackson.internal.jackson.jaxrs.json.JacksonJaxbJsonProvider;
import org.glassfish.jersey.server.ResourceConfig;
import org.glassfish.jersey.servlet.ServletContainer;
import org.slf4j.MDC;

/**
 * Performs any required initialization logic on application context start.
 */
@Singleton
@Requires(notEnv = {Environment.TEST})
@Slf4j
public class ServerApplicationInitializer  implements ApplicationEventListener<ServiceReadyEvent> {

  @Override public void onApplicationEvent(final ServiceReadyEvent event) {
    final Server server = new Server(PORT);

    final ServletContextHandler handler = new ServletContextHandler();

    final Map<String, String> mdc = MDC.getCopyOfContextMap();

    final ResourceConfig rc =
        new ResourceConfig()
            .register(new RequestLogger(mdc))
            .register(InvalidInputExceptionMapper.class)
            .register(InvalidJsonExceptionMapper.class)
            .register(InvalidJsonInputExceptionMapper.class)
            .register(KnownExceptionMapper.class)
            .register(UncaughtExceptionMapper.class)
            .register(NotFoundExceptionMapper.class)
            // needed so that the custom json exception mappers don't get overridden
            // https://stackoverflow.com/questions/35669774/jersey-custom-exception-mapper-for-invalid-json-string
            .register(JacksonJaxbJsonProvider.class);

    // inject custom server functionality
    customComponentClasses.forEach(rc::register);
    customComponents.forEach(rc::register);

    final ServletHolder configServlet = new ServletHolder(new ServletContainer(rc));

    handler.addServlet(configServlet, "/api/*");

    server.setHandler(handler);

    server.start();
    final String banner = MoreResources.readResource("banner/banner.txt");
    LOGGER.info(banner + String.format("Version: %s\n", airbyteVersion.serialize()));
    server.join();

    Runtime.getRuntime().addShutdownHook(new Thread(() -> {
      try {
        server.stop();
      } catch (final Exception ex) {
        // silently fail at this stage because server is terminating.
        LOGGER.warn("exception: " + ex);
      }
    }));
  }
}
