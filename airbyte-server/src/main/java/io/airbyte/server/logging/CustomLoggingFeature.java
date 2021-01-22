package io.airbyte.server.logging;

import org.glassfish.jersey.internal.inject.Custom;
import org.glassfish.jersey.logging.LoggingFeature;

import javax.ws.rs.core.Feature;
import javax.ws.rs.core.FeatureContext;

public class CustomLoggingFeature implements Feature {
    public CustomLoggingFeature() {

    }

    @Override
    public boolean configure(FeatureContext context) {
        return false;
    }
}
