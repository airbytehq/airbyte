package io.airbyte.server.auth;

import jakarta.inject.Singleton;
import java.util.Collection;
import java.util.List;

@Singleton
public class PermissionService {

  public Collection<String> getUserPermissions(final String username) {
    return List.of("ADMIN", "EDITOR", "READER");
  }
}
