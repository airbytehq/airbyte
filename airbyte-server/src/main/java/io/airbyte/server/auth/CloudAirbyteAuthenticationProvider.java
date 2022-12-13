package io.airbyte.server.auth;

import io.micronaut.context.annotation.Replaces;
import io.micronaut.http.HttpRequest;
import io.micronaut.security.authentication.AuthenticationProvider;
import io.micronaut.security.authentication.AuthenticationRequest;
import io.micronaut.security.authentication.AuthenticationResponse;
import jakarta.inject.Singleton;
import java.util.Collection;
import lombok.extern.slf4j.Slf4j;
import org.reactivestreams.Publisher;
import reactor.core.publisher.Flux;

@Singleton
@Replaces(bean=AirbyteAuthenticationProvider.class)
@Slf4j
public class CloudAirbyteAuthenticationProvider implements AuthenticationProvider {

  private final PermissionService permissionService;

  public CloudAirbyteAuthenticationProvider(final PermissionService permissionService) {
    this.permissionService = permissionService;
  }

  @Override
  public Publisher<AuthenticationResponse> authenticate(final HttpRequest<?> httpRequest, final AuthenticationRequest<?, ?> authenticationRequest) {
    log.info("Authenticating identity {}...", authenticationRequest.getIdentity());

    final String username = (String)authenticationRequest.getIdentity();
    final Collection<String> roles = permissionService.getUserPermissions(username);
    log.info("Got roles {} for user {}.", roles, username);
    final AuthenticationResponse authenticationResponse = AuthenticationResponse.success(username, roles);

    return Flux.create(emitter -> {
      emitter.next(authenticationResponse);
      emitter.complete();
    });
  }
}
