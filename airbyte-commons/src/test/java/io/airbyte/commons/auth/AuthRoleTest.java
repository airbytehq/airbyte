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
    final Set<AuthRole> ownerResult = AuthRole.buildAuthRolesSet(AuthRole.OWNER);
    assertEquals(5, ownerResult.size());
    assertEquals(Set.of(AuthRole.OWNER, AuthRole.ADMIN, AuthRole.EDITOR, AuthRole.READER, AuthRole.AUTHENTICATED_USER), ownerResult);

    final Set<AuthRole> adminResult = AuthRole.buildAuthRolesSet(AuthRole.ADMIN);
    assertEquals(4, adminResult.size());
    assertEquals(Set.of(AuthRole.ADMIN, AuthRole.EDITOR, AuthRole.READER, AuthRole.AUTHENTICATED_USER), adminResult);

    final Set<AuthRole> editorResult = AuthRole.buildAuthRolesSet(AuthRole.EDITOR);
    assertEquals(3, editorResult.size());
    assertEquals(Set.of(AuthRole.EDITOR, AuthRole.READER, AuthRole.AUTHENTICATED_USER), editorResult);

    final Set<AuthRole> readerResult = AuthRole.buildAuthRolesSet(AuthRole.READER);
    assertEquals(2, readerResult.size());
    assertEquals(Set.of(AuthRole.READER, AuthRole.AUTHENTICATED_USER), readerResult);

    final Set<AuthRole> authenticatedUserResult = AuthRole.buildAuthRolesSet(AuthRole.AUTHENTICATED_USER);
    assertEquals(1, authenticatedUserResult.size());
    assertEquals(Set.of(AuthRole.AUTHENTICATED_USER), authenticatedUserResult);

    final Set<AuthRole> noneResult = AuthRole.buildAuthRolesSet(AuthRole.NONE);
    assertEquals(1, noneResult.size());
    assertEquals(Set.of(AuthRole.NONE), noneResult);

    final Set<AuthRole> nullResult = AuthRole.buildAuthRolesSet(null);
    assertEquals(0, nullResult.size());
  }
}
