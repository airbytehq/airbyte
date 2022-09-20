/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.config;

import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTCreator;
import com.auth0.jwt.algorithms.Algorithm;
import com.google.auth.oauth2.ServiceAccountCredentials;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.config.Configs.WorkerPlane;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Value;
import java.io.FileInputStream;
import java.net.http.HttpClient;
import java.net.http.HttpClient.Version;
import java.security.interfaces.RSAPrivateKey;
import java.util.Date;
import java.util.concurrent.TimeUnit;
import javax.inject.Named;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

/**
 * Micronaut bean factory for API client singletons.
 */
@Factory
@Slf4j
public class ApiClientBeanFactory {

  private static final int JWT_TTL_MINUTES = 5;

  @Singleton
  public AirbyteApiClient airbyteApiClient(
                                           @Value("${airbyte.internal.api.auth-header.name}") final String airbyteApiAuthHeaderName,
                                           @Value("${airbyte.internal.api.host}") final String airbyteApiHost,
                                           @Named("internalApiAuthToken") final String internalApiAuthToken,
                                           @Named("internalApiScheme") final String internalApiScheme) {
    return new AirbyteApiClient(
        new io.airbyte.api.client.invoker.generated.ApiClient()
            .setScheme(internalApiScheme)
            .setHost(parseHostName(airbyteApiHost))
            .setPort(parsePort(airbyteApiHost))
            .setBasePath("/api")
            .setHttpClientBuilder(HttpClient.newBuilder().version(Version.HTTP_1_1))
            .setRequestInterceptor(builder -> {
              builder.setHeader("User-Agent", "WorkerApp");
              if (!airbyteApiAuthHeaderName.isBlank()) {
                builder.setHeader(airbyteApiAuthHeaderName, internalApiAuthToken);
              }
            }));
  }

  @Singleton
  @Named("internalApiScheme")
  public String internalApiScheme(final WorkerPlane workerPlane) {
    // control plane workers communicate with the Airbyte API within their internal network, so https
    // isn't needed
    return WorkerPlane.CONTROL_PLANE.equals(workerPlane) ? "http" : "https";
  }

  /**
   * Generate an auth token based on configs. This is called by the Api Client's requestInterceptor
   * for each request.
   * <p>
   * For Data Plane workers, generate a signed JWT as described here:
   * https://cloud.google.com/endpoints/docs/openapi/service-account-authentication
   * <p>
   * Otherwise, use the AIRBYTE_API_AUTH_HEADER_VALUE from EnvConfigs.
   */
  @Singleton
  @Named("internalApiAuthToken")
  public String internalApiAuthToken(
                                     @Value("${airbyte.internal.api.auth-header.value}") final String airbyteApiAuthHeaderValue,
                                     @Value("${airbyte.control.plane.auth-endpoint}") final String controlPlaneAuthEndpoint,
                                     @Value("${airbyte.data.plane.service-account.email}") final String dataPlaneServiceAccountEmail,
                                     @Value("${airbyte.data.plane.service-account.credentials-path}") final String dataPlaneServiceAccountCredentialsPath,
                                     final WorkerPlane workerPlane) {
    if (WorkerPlane.CONTROL_PLANE.equals(workerPlane)) {
      // control plane workers communicate with the Airbyte API within their internal network, so a signed
      // JWT isn't needed
      return airbyteApiAuthHeaderValue;
    } else if (WorkerPlane.DATA_PLANE.equals(workerPlane)) {
      try {
        final Date now = new Date();
        final Date expTime = new Date(System.currentTimeMillis() + TimeUnit.MINUTES.toMillis(JWT_TTL_MINUTES));
        // Build the JWT payload
        final JWTCreator.Builder token = JWT.create()
            .withIssuedAt(now)
            .withExpiresAt(expTime)
            .withIssuer(dataPlaneServiceAccountEmail)
            .withAudience(controlPlaneAuthEndpoint)
            .withSubject(dataPlaneServiceAccountEmail)
            .withClaim("email", dataPlaneServiceAccountEmail);

        // TODO multi-cloud phase 2: check performance of on-demand token generation in load testing. might
        // need to pull some of this outside of this method which is called for every API request
        final FileInputStream stream = new FileInputStream(dataPlaneServiceAccountCredentialsPath);
        final ServiceAccountCredentials cred = ServiceAccountCredentials.fromStream(stream);
        final RSAPrivateKey key = (RSAPrivateKey) cred.getPrivateKey();
        final Algorithm algorithm = Algorithm.RSA256(null, key);
        return "Bearer " + token.sign(algorithm);
      } catch (final Exception e) {
        log.warn(
            "An issue occurred while generating a data plane auth token. Defaulting to empty string. Error Message: {}",
            e.getMessage());
        return "";
      }
    } else {
      log.warn("Worker somehow wasn't a control plane or a data plane worker!");
      return "";
    }
  }

  private String parseHostName(final String airbyteInternalApiHost) {
    return airbyteInternalApiHost.split(":")[0];
  }

  private int parsePort(final String airbyteInternalApiHost) {
    return Integer.parseInt(airbyteInternalApiHost.split(":")[1]);
  }

}
