import posthog, { PostHog } from "posthog-js";
import { useContext, useEffect } from "react";
import React from "react";

import { useConfig } from "config";

interface Context {
  posthog: PostHog;
  featureFlagsVariants?: Record<string, boolean | string>;
}
const postHogServiceContext = React.createContext<Context | null>(null);
const PostHogServiceProvider = postHogServiceContext.Provider;

export const PostHogProvider = ({ children }: { children: React.ReactNode }) => {
  const { postHog: posthogKey } = useConfig();

  useEffect(() => {
    if (posthogKey) {
      posthog.init(posthogKey, { api_host: "https://app.posthog.com" });
    }
  }, []);

  if (posthogKey) {
    return <PostHogServiceProvider value={{ posthog }}>{children}</PostHogServiceProvider>;
  }

  return <>{children}</>;
};

export const usePostHog = () => {
  const posthogContext = useContext(postHogServiceContext);

  if (!posthogContext) {
    throw new Error("posthogContext must be used within a PostHogProvider.");
  }

  return posthogContext;
};
