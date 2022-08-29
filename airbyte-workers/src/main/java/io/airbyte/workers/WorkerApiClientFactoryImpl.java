/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTCreator;
import com.auth0.jwt.algorithms.Algorithm;
import com.google.auth.oauth2.ServiceAccountCredentials;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerPlane;
import java.io.FileInputStream;
import java.security.interfaces.RSAPrivateKey;
import java.util.Date;
import java.util.concurrent.TimeUnit;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class WorkerApiClientFactoryImpl implements WorkerApiClientFactory {

  private static final int JWT_TTL_MINUTES = 5;

  private final AirbyteApiClient airbyteApiClient;

  public WorkerApiClientFactoryImpl(final Configs configs) {
    final var authHeader = configs.getAirbyteApiAuthHeaderName();

    // control plane workers communicate with the Airbyte API within their internal network, so https
    // isn't needed
    final var scheme = configs.getWorkerPlane().equals(WorkerPlane.CONTROL_PLANE) ? "http" : "https";

    log.debug("Creating Airbyte Config Api Client with Scheme: {}, Host: {}, Port: {}, Auth-Header: {}",
        scheme, configs.getAirbyteApiHost(), configs.getAirbyteApiPort(), authHeader);

    this.airbyteApiClient = new AirbyteApiClient(
        new io.airbyte.api.client.invoker.generated.ApiClient()
            .setScheme(scheme)
            .setHost(configs.getAirbyteApiHost())
            .setPort(configs.getAirbyteApiPort())
            .setBasePath("/api")
            .setRequestInterceptor(builder -> {
              builder.setHeader("User-Agent", "WorkerApp");
              if (!authHeader.isBlank()) {
                builder.setHeader(authHeader, generateAuthToken(configs));
              }
            }));
  }

  @Override
  public AirbyteApiClient create() {
    return this.airbyteApiClient;
  }

  /**
   * Generate an auth token based on configs. This is called by the Api Client's requestInterceptor
   * for each request.
   *
   * For Data Plane workers, generate a signed JWT as described here:
   * https://cloud.google.com/endpoints/docs/openapi/service-account-authentication
   *
   * Otherwise, use the AIRBYTE_API_AUTH_HEADER_VALUE from EnvConfigs.
   */
  private static String generateAuthToken(final Configs configs) {
    if (configs.getWorkerPlane().equals(WorkerPlane.CONTROL_PLANE)) {
      // control plane workers communicate with the Airbyte API within their internal network, so a signed
      // JWT isn't needed
      return configs.getAirbyteApiAuthHeaderValue();
    } else if (configs.getWorkerPlane().equals(WorkerPlane.DATA_PLANE)) {
      try {
        final Date now = new Date();
        final Date expTime = new Date(System.currentTimeMillis() + TimeUnit.MINUTES.toMillis(JWT_TTL_MINUTES));
        final String saEmail = configs.getDataPlaneServiceAccountEmail();
        // Build the JWT payload
        final JWTCreator.Builder token = JWT.create()
            .withIssuedAt(now)
            .withExpiresAt(expTime)
            .withIssuer(saEmail)
            .withAudience(configs.getControlPlaneAuthEndpoint())
            .withSubject(saEmail)
            .withClaim("email", saEmail);

        // TODO multi-cloud phase 2: check performance of on-demand token generation in load testing. might
        // need to pull some of this outside of this method which is called for every API request
        final FileInputStream stream = new FileInputStream(configs.getDataPlaneServiceAccountCredentialsPath());
        final ServiceAccountCredentials cred = ServiceAccountCredentials.fromStream(stream);
        final RSAPrivateKey key = (RSAPrivateKey) cred.getPrivateKey();
        final Algorithm algorithm = Algorithm.RSA256(null, key);
        return "Bearer " + token.sign(algorithm);
      } catch (final Exception e) {
        log.warn("An issue occurred while generating a data plane auth token. Defaulting to empty string.", e);
        return "";
      }
    } else {
      log.warn("Worker somehow wasn't a control plane or a data plane worker!");
      return "";
    }
  }

}
