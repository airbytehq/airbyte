/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.auth;

import io.micrometer.common.util.StringUtils;
import io.micronaut.context.annotation.Replaces;
import io.micronaut.http.HttpRequest;
import io.micronaut.security.authentication.AuthenticationException;
import io.micronaut.security.authentication.AuthenticationProvider;
import io.micronaut.security.authentication.AuthenticationRequest;
import io.micronaut.security.authentication.AuthenticationResponse;
import jakarta.inject.Singleton;
import java.util.Collection;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;
import org.reactivestreams.Publisher;
import reactor.core.publisher.Flux;

@Singleton
@Replaces(bean = AirbyteAuthenticationProvider.class)
@Slf4j
public class CloudAirbyteAuthenticationProvider implements AuthenticationProvider {

  private final PermissionService permissionService;

  public CloudAirbyteAuthenticationProvider(final PermissionService permissionService) {
    this.permissionService = permissionService;
  }

  @Override
  public Publisher<AuthenticationResponse> authenticate(final HttpRequest<?> httpRequest, final AuthenticationRequest<?, ?> authenticationRequest) {
    log.info("{} invoked.", getClass().getName());
    return Flux.create(emitter -> {
      emitter.next(authenticateRequest(httpRequest, authenticationRequest));
      emitter.complete();
    });
  }

  private AuthenticationResponse authenticateRequest(final HttpRequest<?> httpRequest, final AuthenticationRequest<?, ?> authenticationRequest) {
    log.info("Authenticating identity {}...", authenticationRequest.getIdentity());

    try {
      final String username = (String) authenticationRequest.getIdentity();
      final Collection<String> roles = getRoles(httpRequest, authenticationRequest);
      log.info("Authenticating user {} with roles {} for URI {}...", username, roles, httpRequest.getUri().getPath());
      return AuthenticationResponse.success(username, roles);
    } catch (final Exception e) {
      log.error("Unable to authenticate request {}.", httpRequest.getUri().getPath(), e);
      return AuthenticationResponse.failure(e.getMessage());
    }
  }

  private Collection<String> getRoles(final HttpRequest<?> httpRequest, final AuthenticationRequest<?, ?> authenticationRequest)
      throws AuthenticationException {
    if (StringUtils.isNotBlank(httpRequest.getHeaders().get(AuthorizationServerHandler.WORKSPACE_ID_HEADER))) {
      return getWorkspaceRoles(httpRequest);
    } else {
      return getUserRoles(authenticationRequest);
    }
  }

  private Collection<String> getUserRoles(final AuthenticationRequest<?, ?> authenticationRequest) throws AuthenticationException {
    log.info("Retrieving user roles for user '{}'...", authenticationRequest.getIdentity());
    return permissionService.getUserPermissions((String) authenticationRequest.getIdentity());
  }

  private Collection<String> getWorkspaceRoles(final HttpRequest<?> httpRequest) throws AuthenticationException {
    final String workspaceId = httpRequest.getHeaders().get(AuthorizationServerHandler.WORKSPACE_ID_HEADER);
    log.info("Retrieving workspace roles for workspace '{}'...", workspaceId);
    return permissionService.getWorkspacePermissions(UUID.fromString(workspaceId));
  }

}
