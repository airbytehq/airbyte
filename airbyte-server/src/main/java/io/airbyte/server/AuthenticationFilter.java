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

public class AuthenticationFilter implements ContainerRequestFilter {

    private static final String REALM = "Bearer <BLOTOUT_TOKEN>";
    private static final String AUTHENTICATION_SCHEME = "Bearer";
    private static final Logger LOGGER = LoggerFactory.getLogger(ServerApp.class);

    private final BlotoutAuthentication blotoutAuthentication = new BlotoutAuthentication();

    @Override
    public void filter(ContainerRequestContext requestContext) throws IOException {
        if (!"v1/health".equalsIgnoreCase(requestContext.getUriInfo().getPath())) {
            // Get the Authorization header from the request
            String authorizationHeader =
                    requestContext.getHeaderString(HttpHeaders.AUTHORIZATION);
            // Validate the Authorization header
            if (requestContext.getMethod().equalsIgnoreCase("OPTIONS")) {
                requestContext.abortWith(Response.ok().build());
                return;
            }
            if (!isTokenBasedAuthentication(authorizationHeader)) {
                abortWithUnauthorized(requestContext);
                LOGGER.error(" return from isTokenBasedAuthentication ");
                return;
            }
            // Extract the token from the Authorization header
            String token = authorizationHeader
                    .substring(AUTHENTICATION_SCHEME.length()).trim();
            LOGGER.info(" Token " + token);
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
        }
    }

    private boolean isTokenBasedAuthentication(String authorizationHeader) {
        // Check if the Authorization header is valid
        // It must not be null and must be prefixed with "Bearer" plus a whitespace
        // The authentication scheme comparison must be case-insensitive
        return authorizationHeader != null && authorizationHeader.toLowerCase()
                .startsWith(AUTHENTICATION_SCHEME.toLowerCase() + " ");
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

}