package io.airbyte.server.auth;

import jakarta.inject.Singleton;
import java.util.Collection;
import java.util.List;
import java.util.Set;

@Singleton
public class PermissionService {

  public static final Collection<String> ROLES = Set.of("OWNER", "ADMIN", "EDITOR", "READER", "AUTHENTICATED_USER", "NONE");

  public Collection<String> getUserPermissions(final String username) {
    return Set.of("EDITOR", "READER");
  }
}
