package io.airbyte.commons.auth;

import java.util.Comparator;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * This enum describes the standard auth levels for a given resource. It currently is only used for 2
 * resources Workspace and Instance (i.e. the entire instance or deployment of Airbyte).
 *
 * In the context of a workspace, there is a 1:1 mapping.
 * <ul>
 * <li>OWNER => WORKSPACE OWNER. Superadmin of the instance (typically the person that created it),
 * has all the rights on the instance including deleting it.</li>
 * <li>ADMIN => WORKSPACE ADMIN. Admin of the instance, can invite other users, update their
 * permission and change settings of the instance.</li>
 * <li>EDITOR => WORKSPACE EDITOR</li>
 * <li>READER => WORKSPACE READER</li>
 * <li>AUTHENTICATED_USER => INVALID</li>
 * <li>NONE => NONE (does not have access to this resource)</li>
 * </ul>
 * In the context of the instance, there are currently only 3 levels.
 * <ul>
 * <li>ADMIN => INSTANCE ADMIN</li>
 * <li>AUTHENTICATED_USER => Denotes that all that is required for access is an active Airbyte
 * account. This should only ever be used when the associated resource is an INSTANCE. All other
 * uses are invalid. It is a special value in the enum to handle a case that only applies to
 * instances and no other resources.</li>
 * <li>NONE => NONE (not applicable. anyone being checked in our auth stack already has an account
 * so by definition they have some access to the instance.)</li>
 * </ul>
 */
public enum AuthRole {

  OWNER(500),
  ADMIN(400),
  EDITOR(300),
  READER(200),
  AUTHENTICATED_USER(100), // ONLY USE WITH INSTANCE RESOURCE!
  NONE(0);

  private final int authority;

  AuthRole(final int authority) {
    this.authority = authority;
  }

  public int getAuthority() {
    return authority;
  }

  /**
   * Builds the set of roles based on the provided {@link AuthRole} value.
   * <p>
   * The generated set of auth roles contains the provided {@link AuthRole} (if not {@code null})
   * and any other authentication roles with a lesser {@link #getAuthority()} value.
   * </p>
   *
   * @param authRole An {@link AuthRole} (may be {@code null}).
   * @return The set of {@link AuthRole}s based on the provided {@link AuthRole}.
   */
  public static Set<AuthRole> buildAuthRolesSet(final AuthRole authRole) {
    final Set<AuthRole> authRoles = new HashSet<>();

    if(authRole != null) {
      authRoles.add(authRole);
      authRoles.addAll(Stream.of(values())
          .filter(role -> !NONE.equals(role))
          .filter(role -> role.getAuthority() < authRole.getAuthority())
          .collect(Collectors.toSet()));
    }

    // Sort final set by descending authority order
    return authRoles.stream()
        .sorted(Comparator.comparingInt(AuthRole::getAuthority))
        .collect(Collectors.toCollection(LinkedHashSet::new));
  }

}
