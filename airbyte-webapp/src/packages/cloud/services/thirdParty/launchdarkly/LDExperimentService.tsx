import * as LDClient from "launchdarkly-js-client-sdk";
import { useEffect, useRef, useState } from "react";

import { LoadingPage } from "components";

import { useConfig } from "config";
import { ExperimentProvider, ExperimentService } from "hooks/services/Experiment";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";

import { useAuthService } from "../../auth/AuthService";

/**
 * The maximum time in milliseconds we'll wait for LaunchDarkly to finish initialization,
 * before running disabling it.
 */
const INITIALIZATION_TIMEOUT = 1000;

type LDInitState = "initializing" | "failed" | "initialized";

/**
 * Returns a promise that rejects after `delay` milliseconds with the given reason.
 */
function rejectAfter(delay: number, reason: string) {
  return new Promise((_, reject) => {
    window.setTimeout(() => reject(reason), delay);
  });
}

const LDInitializationWrapper: React.FC<{ apiKey: string }> = ({ children, apiKey }) => {
  const ldClient = useRef<LDClient.LDClient>();
  const [state, setState] = useState<LDInitState>("initializing");
  const { user } = useAuthService();
  const workspaceId = useCurrentWorkspaceId();

  if (!ldClient.current) {
    ldClient.current = LDClient.initialize(apiKey, { anonymous: true });
    // Wait for either LaunchDarkly to initialize or a specific timeout to pass first
    Promise.race([
      ldClient.current.waitForInitialization(),
      rejectAfter(INITIALIZATION_TIMEOUT, "Timed out waiting for LaunchDarkly to initialize"),
    ])
      .then(() => {
        // The LaunchDarkly promise resolved before the timeout, so we're good to use LD.
        setState("initialized");
      })
      .catch((reason) => {
        // If the promise fails, either because LaunchDarkly service fails to initialize, or
        // our timeout promise resolves first, we're going to show an error and assume the service
        // failed to initialize, i.e. we'll run without it.
        console.warn(`Failed to initialize LaunchDarkly service with reason: ${String(reason)}`);
        setState("failed");
      });
  }

  useEffect(() => {
    console.log("User information changed", user, workspaceId);
    if (user) {
      ldClient.current?.identify({
        key: user.userId,
        email: user.email,
        name: user.name,
        custom: { intercomHash: user.intercomHash },
        anonymous: false,
      });
    } else {
      ldClient.current?.identify({ anonymous: true });
    }
  }, [user, workspaceId]);

  if (state === "initializing") {
    return <LoadingPage />;
  }

  if (state === "failed") {
    return <>{children}</>;
  }

  const getExperiment: ExperimentService["getExperiment"] = (key, defaultValue) => {
    return ldClient.current?.variation(key, defaultValue);
  };

  return <ExperimentProvider value={{ getExperiment }}>{children}</ExperimentProvider>;
};

export const LDExperimentServiceProvider: React.FC = ({ children }) => {
  console.log("LDExperimentServiceProvider");
  const { launchdarkly: launchdarklyKey } = useConfig();

  return !launchdarklyKey ? (
    <>{children}</>
  ) : (
    <LDInitializationWrapper apiKey={launchdarklyKey}>{children}</LDInitializationWrapper>
  );
};
