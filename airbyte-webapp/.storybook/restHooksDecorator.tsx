import { Fixture, MockResolver } from "@rest-hooks/test";
import { CacheProvider } from "@rest-hooks/core";
import { Suspense } from "react";
import { NetworkErrorBoundary } from "rest-hooks";

const fixtures: Fixture[] = [];

export const MockDecorator = (getStory) => (
  <CacheProvider>
    <Suspense fallback="loading">
      <NetworkErrorBoundary>
        <MockResolver fixtures={fixtures}>{getStory()}</MockResolver>
      </NetworkErrorBoundary>
    </Suspense>
  </CacheProvider>
);
