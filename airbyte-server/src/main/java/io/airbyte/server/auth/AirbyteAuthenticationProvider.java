package io.airbyte.server.auth;

import io.micronaut.context.annotation.Value;
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
@Slf4j
@SuppressWarnings({"PMD.UnusedPrivateField"})
public class AirbyteAuthenticationProvider implements AuthenticationProvider {

  private final PermissionService permissionService;

  private final String stubUserId;

  // curl -i -u airbyte:password -X POST -H 'Content-Type: application/json'
  // -d '{"workspaceId":"905227ae-a350-4cc7-be6b-f936e00e53cb"}' http://localhost:8080/api/v1/connections/list

  public AirbyteAuthenticationProvider(final PermissionService permissionService,
      @Value("${airbyte.stub.user.id:health-check}") final String stubUserId) {
    this.permissionService = permissionService;
    this.stubUserId = stubUserId;
  }

  @Override
  public Publisher<AuthenticationResponse> authenticate(final HttpRequest<?> httpRequest, final AuthenticationRequest<?, ?> authenticationRequest) {
    log.info("Authenticating identity {}...", authenticationRequest.getIdentity());

//    if (NO_AUTH_CHECK_ROUTES.contains(httpRequest.getUri().getPath())) {
//      return Flux.create(emitter -> {
//        emitter.next(AuthenticationResponse.success(stubUserId));
//        emitter.complete();
//      });
//    }

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
