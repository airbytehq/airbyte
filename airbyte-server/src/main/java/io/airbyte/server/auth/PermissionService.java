/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.auth;

import io.airbyte.commons.auth.AuthRole;
import jakarta.inject.Singleton;
import java.util.Collection;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

@Singleton
public class PermissionService {

  public Collection<String> getUserPermissions(final String username) {
    return AuthRole.buildAuthRolesSet(AuthRole.EDITOR).stream().map(r -> r.name()).collect(Collectors.toSet());
  }

  public Collection<String> getWorkspacePermissions(final UUID workspaceId) {
    return Set.of(AuthRole.OWNER.name());
  }

}
