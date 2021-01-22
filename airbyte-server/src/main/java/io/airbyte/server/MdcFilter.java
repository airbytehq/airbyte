package io.airbyte.server;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

import javax.ws.rs.container.ContainerRequestContext;
import javax.ws.rs.container.ContainerResponseContext;
import javax.ws.rs.container.ContainerResponseFilter;
import java.util.Map;

public class MdcFilter implements ContainerResponseFilter {
    private final Map<String, String> mdc;

    public MdcFilter(Map<String, String> mdc) {
        this.mdc = mdc;
    }

    @Override
    public void filter(ContainerRequestContext requestContext, ContainerResponseContext responseContext) {
        MDC.setContextMap(mdc);
    }
}
