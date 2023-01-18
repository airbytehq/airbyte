import { lazy, Suspense } from "react";

import { InviteUsersHintProps } from "packages/cloud/views/users/InviteUsersHint/types";
import { isCloudApp } from "utils/app";

const LazyInviteUsersHint = lazy(() =>
  import("packages/cloud/views/users/InviteUsersHint").then(({ InviteUsersHint }) => ({ default: InviteUsersHint }))
);

export const CloudInviteUsersHint: React.VFC<InviteUsersHintProps> = (props) =>
  isCloudApp() ? (
    <Suspense fallback={null}>
      <LazyInviteUsersHint {...props} />
    </Suspense>
  ) : null;
