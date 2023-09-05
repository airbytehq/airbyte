package io.airbyte.server.enums;

import java.util.Arrays;
import java.util.List;

public enum EdgeTagClient {

    EDGETAG("https://api.edgetag.io"), EDGETAG_SANDBOX("https://api-sandbox.edgetag.io");

    private String edgeTagOrigin;

    EdgeTagClient(String edgeTagOrigin) { this.edgeTagOrigin = edgeTagOrigin; }

    public String getEdgeTagOrigin() { return edgeTagOrigin; }

    protected static final List<String> edgeTagOrigins = Arrays.asList(EdgeTagClient.EDGETAG.getEdgeTagOrigin(),
            EdgeTagClient.EDGETAG_SANDBOX.getEdgeTagOrigin());

    public static List<String> getEdgeTagOrigins() { return edgeTagOrigins; }

}
