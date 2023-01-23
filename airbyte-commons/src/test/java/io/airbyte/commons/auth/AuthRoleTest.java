/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.auth;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Set;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link AuthRole} enumeration.
 */
class AuthRoleTest {

  @Test
  void testBuildingAuthRoleSet() {
    final Set<String> ownerResult = AuthRole.buildAuthRolesSet(AuthRole.OWNER);
    assertEquals(5, ownerResult.size());
    assertEquals(Set.of(AuthRole.OWNER.getLabel(), AuthRole.ADMIN.getLabel(), AuthRole.EDITOR.getLabel(), AuthRole.READER.getLabel(),
        AuthRole.AUTHENTICATED_USER.getLabel()), ownerResult);

    final Set<String> adminResult = AuthRole.buildAuthRolesSet(AuthRole.ADMIN);
    assertEquals(4, adminResult.size());
    assertEquals(Set.of(AuthRole.ADMIN.getLabel(), AuthRole.EDITOR.getLabel(), AuthRole.READER.getLabel(), AuthRole.AUTHENTICATED_USER.getLabel()),
        adminResult);

    final Set<String> editorResult = AuthRole.buildAuthRolesSet(AuthRole.EDITOR);
    assertEquals(3, editorResult.size());
    assertEquals(Set.of(AuthRole.EDITOR.getLabel(), AuthRole.READER.getLabel(), AuthRole.AUTHENTICATED_USER.getLabel()), editorResult);

    final Set<String> readerResult = AuthRole.buildAuthRolesSet(AuthRole.READER);
    assertEquals(2, readerResult.size());
    assertEquals(Set.of(AuthRole.READER.getLabel(), AuthRole.AUTHENTICATED_USER.getLabel()), readerResult);

    final Set<String> authenticatedUserResult = AuthRole.buildAuthRolesSet(AuthRole.AUTHENTICATED_USER);
    assertEquals(1, authenticatedUserResult.size());
    assertEquals(Set.of(AuthRole.AUTHENTICATED_USER.getLabel()), authenticatedUserResult);

    final Set<String> noneResult = AuthRole.buildAuthRolesSet(AuthRole.NONE);
    assertEquals(1, noneResult.size());
    assertEquals(Set.of(AuthRole.NONE.getLabel()), noneResult);

    final Set<String> nullResult = AuthRole.buildAuthRolesSet(null);
    assertEquals(0, nullResult.size());
  }

}
