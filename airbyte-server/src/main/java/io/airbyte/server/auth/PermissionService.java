package io.airbyte.server.auth;

import io.airbyte.commons.auth.AuthRole;
import jakarta.inject.Singleton;
import java.util.Collection;
import java.util.stream.Collectors;

@Singleton
public class PermissionService {

  public Collection<String> getUserPermissions(final String username) {
    return AuthRole.buildAuthRolesSet(AuthRole.EDITOR).stream().map(r -> r.name()).collect(Collectors.toSet());
  }
}
