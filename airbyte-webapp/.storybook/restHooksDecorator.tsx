import { Fixture, MockResolver } from "@rest-hooks/test";
import { CacheProvider } from "@rest-hooks/core";
import { Suspense } from "react";
import { NetworkErrorBoundary } from "rest-hooks";

import WorkspaceResource from "../src/core/resources/Workspace";

const fixtures: Fixture[] = [
  {
    request: WorkspaceResource.detailShape(),
    params: { workspaceId: undefined },
    result: {
      workspaceId: "story-book",
    },
  },
];

export const MockDecorator = (getStory) => (
  <CacheProvider>
    <Suspense fallback="loading">
      <NetworkErrorBoundary>
        <MockResolver fixtures={fixtures}>{getStory()}</MockResolver>
      </NetworkErrorBoundary>
    </Suspense>
  </CacheProvider>
);
