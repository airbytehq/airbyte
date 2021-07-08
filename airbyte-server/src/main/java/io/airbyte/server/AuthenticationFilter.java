/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server;

import io.airbyte.server.services.BlotoutAuthentication;
import java.io.IOException;
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
        LOGGER.error(" return from exception " + e.getCause());
        e.printStackTrace();
        abortWithUnauthorized(requestContext);
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
