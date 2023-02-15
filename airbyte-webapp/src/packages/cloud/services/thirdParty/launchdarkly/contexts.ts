import { LDMultiKindContext, LDSingleKindContext } from "launchdarkly-js-client-sdk";

import { User } from "packages/cloud/lib/domain/users/types";

export function createUserContext(user: User | null, locale: string): LDSingleKindContext {
  const kind = "user";

  if (!user) {
    return {
      kind,
      anonymous: true,
      locale,
      // @ts-expect-error LaunchDarkly's typescript types specify that key must be defined, but actually they handle a null or undefined key. It's even recommended in their docs to omit the key for anonymous users https://docs.launchdarkly.com/sdk/client-side/javascript/migration-2-to-3#understanding-changes-to-anonymous-users
      key: undefined,
    };
  }

  return {
    kind,
    anonymous: false,
    key: user.userId,
    email: user.email,
    name: user.name,
    intercomHash: user.intercomHash,
    locale,
  };
}

export function createWorkspaceContext(workspaceId: string): LDSingleKindContext {
  return {
    kind: "workspace",
    key: workspaceId,
  };
}

export function createMultiContext(...args: LDSingleKindContext[]): LDMultiKindContext {
  const multiContext: LDMultiKindContext = {
    kind: "multi",
  };

  args.forEach(({ kind, ...context }) => {
    multiContext[kind] = { ...context };
  });

  return multiContext;
}
