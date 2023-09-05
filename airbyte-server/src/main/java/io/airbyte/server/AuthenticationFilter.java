package io.airbyte.server;

import io.airbyte.server.services.BlotoutAuthentication;

import java.io.IOException;
import javax.annotation.security.PermitAll;
import javax.ws.rs.container.ContainerRequestContext;
import javax.ws.rs.container.ContainerRequestFilter;
import javax.ws.rs.core.HttpHeaders;
import javax.ws.rs.core.Response;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import io.airbyte.server.enums.EdgeTagClient;

public class AuthenticationFilter implements ContainerRequestFilter {

    private static final String REALM = "Bearer <BLOTOUT_TOKEN>";
    private static final String AUTHENTICATION_SCHEME = "Bearer";
    private static final String EDGETAG_ORIGIN = "https://api.edgetag.io";
    private static final Logger LOGGER = LoggerFactory.getLogger(ServerApp.class);

    private final BlotoutAuthentication blotoutAuthentication = new BlotoutAuthentication();

    @Override
    public void filter(ContainerRequestContext requestContext) throws IOException {
        if (!"v1/health".equalsIgnoreCase(requestContext.getUriInfo().getPath())) {
            // Get the Authorization header from the request
            String authorizationHeader =
                    requestContext.getHeaderString(HttpHeaders.AUTHORIZATION);
            // Extract the token from the Authorization header
            String token = authorizationHeader
                    .substring(AUTHENTICATION_SCHEME.length()).trim();

            // Validate the Authorization header
            if (requestContext.getMethod().equalsIgnoreCase("OPTIONS")) {
                requestContext.abortWith(Response.ok().build());
                return;
            }
            // Validate origin based authentication
            String originHeader =
                    requestContext.getHeaderString("origin");
            if (isEdgeTagBasedAuthentication(originHeader)) {
                try {
                    if (!validateEdgeBasedToken(originHeader, token)) {
                        abortWithUnauthorized(requestContext);
                        LOGGER.error(" return from validateEdgeBasedToken ");
                        return;
                    }
                } catch (Exception e) {
                    try {
                        if (!validateEdgeBasedToken(originHeader, token)) {
                            abortWithUnauthorized(requestContext);
                            LOGGER.error(" return from validateEdgeBasedToken ");
                            return;
                        }
                    } catch (Exception e1) {
                        LOGGER.error(" return from inner exception " + e1.getCause());
                        e1.printStackTrace();
                        abortWithUnauthorized(requestContext);
                    }
                }
            } else if (isTokenBasedAuthentication(authorizationHeader)) {
                try {
                    if (!validateToken(token)) {
                        abortWithUnauthorized(requestContext);
                        LOGGER.error(" return from validateToken ");
                        return;
                    }
                } catch (Exception e) {
                    try {
                        if (!validateToken(token)) {
                            abortWithUnauthorized(requestContext);
                            LOGGER.error(" return from validateToken ");
                            return;
                        }
                    } catch (Exception e1) {
                        LOGGER.error(" return from inner exception " + e1.getCause());
                        e1.printStackTrace();
                        abortWithUnauthorized(requestContext);
                    }
                }
            } else {
                abortWithUnauthorized(requestContext);
                LOGGER.error(" return from isTokenBasedAuthentication ");
                return;
            }
        }
    }

    private boolean isTokenBasedAuthentication(String authorizationHeader) {
        // Check if the Authorization header is valid
        // It must not be null and must be prefixed with "Bearer" plus a whitespace
        // The authentication scheme comparison must be case-insensitive
        return authorizationHeader != null && authorizationHeader.toLowerCase()
                .startsWith(AUTHENTICATION_SCHEME.toLowerCase() + " ");
    }

    private boolean isEdgeTagBasedAuthentication(String originHeader) {
        return originHeader != null &&
                EdgeTagClient.getEdgeTagOrigins().contains(originHeader);
    }

    private void abortWithUnauthorized(ContainerRequestContext requestContext) {
        // Abort the filter chain with a 401 status code response
        // The WWW-Authenticate header is sent along with the response
        requestContext.abortWith(
                Response.status(Response.Status.UNAUTHORIZED)
                        .header(HttpHeaders.WWW_AUTHENTICATE,
                                AUTHENTICATION_SCHEME + " realm=\"" + REALM + "\"")
                        .build());
    }

    private boolean validateToken(String token) throws Exception {
        // Checking token from blotout
        return blotoutAuthentication.validateToken(token);
    }

    private boolean validateEdgeBasedToken(String origin, String token) throws Exception {
        return blotoutAuthentication.validateEdgeTagBasedAuthentication(origin, token);
    }

}