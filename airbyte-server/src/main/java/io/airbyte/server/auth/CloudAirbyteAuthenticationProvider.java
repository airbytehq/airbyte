/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.auth;

import io.airbyte.commons.auth.AuthRole;
import io.micrometer.core.instrument.util.StringUtils;
import io.micronaut.context.annotation.Replaces;
import io.micronaut.http.HttpRequest;
import io.micronaut.security.authentication.AuthenticationException;
import io.micronaut.security.authentication.AuthenticationProvider;
import io.micronaut.security.authentication.AuthenticationRequest;
import io.micronaut.security.authentication.AuthenticationResponse;
import jakarta.inject.Singleton;
import java.util.Collection;
import java.util.HashSet;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;
import org.reactivestreams.Publisher;
import reactor.core.publisher.Flux;

@Singleton
@Replaces(bean = AirbyteAuthenticationProvider.class)
@Slf4j
public class CloudAirbyteAuthenticationProvider implements AuthenticationProvider {

  private static final String WORKSPACE_ID_PARAMETER = "workspaceId";

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
      final Collection<String> userRoles = permissionService.getUserPermissions(username);
      log.info("Got user roles {} for user {}.", userRoles, username);

      final Collection<String> workspaceRoles = getWorkspaceRoles(httpRequest);
      log.info("Got workspace roles {}.", workspaceRoles);

      final Collection<String> roles = Stream.concat(userRoles.stream(), workspaceRoles.stream()).collect(Collectors.toSet());
      log.info("Authenticating user {} with roles {} for URI {}...", username, roles, httpRequest.getUri().getPath());

      return AuthenticationResponse.success(username, roles);
    } catch (final Exception e) {
      log.error("Unable to authenticate request {}.", httpRequest.getUri().getPath(), e);
      return AuthenticationResponse.failure(e.getMessage());
    }
  }

  private Collection<String> getWorkspaceRoles(final HttpRequest<?> httpRequest) throws AuthenticationException {
    final Collection<String> roles = new HashSet<>();

    if(StringUtils.isNotBlank(httpRequest.getParameters().get(WORKSPACE_ID_PARAMETER))) {
      final String workspaceId = httpRequest.getParameters().get(WORKSPACE_ID_PARAMETER);
      log.info("Found workspace ID value {} for request {}.", workspaceId, httpRequest.getUri());
      roles.addAll(permissionService.getWorkspacePermissions(UUID.fromString(workspaceId)));
    }

    return roles;
  }

}
