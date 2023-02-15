import { v4 as uuidV4 } from "uuid";

import { User } from "packages/cloud/lib/domain/users";

import { createMultiContext, createUserContext, createWorkspaceContext } from "./contexts";

const mockLocale = "en";

describe(`${createUserContext.name}`, () => {
  it("creates an anonymous user context", () => {
    const context = createUserContext(null, mockLocale);
    expect(context).toEqual({
      kind: "user",
      anonymous: true,
      locale: mockLocale,
    });
  });

  it("creates an identified user context", () => {
    const mockUser: User = {
      userId: uuidV4(),
      name: "John Doe",
      email: "john.doe@airbyte.io",
      intercomHash: "intercom_hash_string",
      authUserId: "auth_user_id_string",
    };
    const context = createUserContext(mockUser, mockLocale);
    expect(context).toEqual({
      kind: "user",
      anonymous: false,
      key: mockUser.userId,
      email: mockUser.email,
      name: mockUser.name,
      intercomHash: mockUser.intercomHash,
      locale: mockLocale,
    });
  });
});

describe(`${createWorkspaceContext.name}`, () => {
  it("creates a workspace context", () => {
    const mockWorkspaceId = uuidV4();
    const context = createWorkspaceContext(mockWorkspaceId);
    expect(context).toEqual({
      kind: "workspace",
      key: mockWorkspaceId,
    });
  });
});

describe(`${createMultiContext.name}`, () => {
  it("creates a workspace context", () => {
    const mockWorkspaceId = uuidV4();
    const userContext = createUserContext(null, mockLocale);
    const workspaceContext = createWorkspaceContext(mockWorkspaceId);
    const multiContext = createMultiContext(userContext, workspaceContext);
    const { kind: userKind, ...userContextWithoutKind } = userContext;
    const { kind: workspaceKind, ...workspaceContextWithoutKind } = workspaceContext;

    expect(multiContext).toEqual({
      kind: "multi",
      user: userContextWithoutKind,
      workspace: workspaceContextWithoutKind,
    });
  });
});
