/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.auth;

import java.util.Comparator;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * This enum describes the standard auth levels for a given resource. It currently is only used for
 * 2 resources Workspace and Instance (i.e. the entire instance or deployment of Airbyte).
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

  OWNER(500, AuthRoleConstants.OWNER),
  ADMIN(400, AuthRoleConstants.ADMIN),
  EDITOR(300, AuthRoleConstants.EDITOR),
  READER(200, AuthRoleConstants.READER),
  AUTHENTICATED_USER(100, AuthRoleConstants.AUTHENTICATED_USER), // ONLY USE WITH INSTANCE RESOURCE!
  NONE(0, AuthRoleConstants.NONE);

  private final int authority;
  private final String label;

  AuthRole(final int authority, final String label) {
    this.authority = authority;
    this.label = label;
  }

  public int getAuthority() {
    return authority;
  }

  public String getLabel() {
    return label;
  }

  /**
   * Builds the set of roles based on the provided {@link AuthRole} value.
   * <p>
   * The generated set of auth roles contains the provided {@link AuthRole} (if not {@code null}) and
   * any other authentication roles with a lesser {@link #getAuthority()} value.
   * </p>
   *
   * @param authRole An {@link AuthRole} (may be {@code null}).
   * @return The set of {@link AuthRole} labels based on the provided {@link AuthRole}.
   */
  public static Set<String> buildAuthRolesSet(final AuthRole authRole) {
    final Set<AuthRole> authRoles = new HashSet<>();

    if (authRole != null) {
      authRoles.add(authRole);
      authRoles.addAll(Stream.of(values())
          .filter(role -> !NONE.equals(role))
          .filter(role -> role.getAuthority() < authRole.getAuthority())
          .collect(Collectors.toSet()));
    }

    // Sort final set by descending authority order
    return authRoles.stream()
        .sorted(Comparator.comparingInt(AuthRole::getAuthority))
        .map(role -> role.getLabel())
        .collect(Collectors.toCollection(LinkedHashSet::new));
  }

}
