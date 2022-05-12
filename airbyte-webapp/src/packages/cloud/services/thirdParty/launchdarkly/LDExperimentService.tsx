import * as LDClient from "launchdarkly-js-client-sdk";
import { useEffect, useRef, useState } from "react";
import { finalize, Subject } from "rxjs";

import { LoadingPage } from "components";

import { useConfig } from "config";
import { ExperimentProvider, ExperimentService } from "hooks/services/Experiment";
import type { Experiments } from "hooks/services/Experiment/experiments";
import { User } from "packages/cloud/lib/domain/users";

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

function mapUserToLDUser(user: User | null): LDClient.LDUser {
  return user
    ? {
        key: user.userId,
        email: user.email,
        name: user.name,
        custom: { intercomHash: user.intercomHash },
        anonymous: false,
      }
    : {
        anonymous: true,
      };
}

const LDInitializationWrapper: React.FC<{ apiKey: string }> = ({ children, apiKey }) => {
  const ldClient = useRef<LDClient.LDClient>();
  const [state, setState] = useState<LDInitState>("initializing");
  const { user } = useAuthService();

  if (!ldClient.current) {
    ldClient.current = LDClient.initialize(apiKey, mapUserToLDUser(user));
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
    ldClient.current?.identify(mapUserToLDUser(user));
  }, [user]);

  if (state === "initializing") {
    return <LoadingPage />;
  }

  if (state === "failed") {
    return <>{children}</>;
  }

  const experimentService: ExperimentService = {
    getExperiment(key, defaultValue) {
      return ldClient.current?.variation(key, defaultValue);
    },
    getExperimentChanges$<K extends keyof Experiments>(key: K) {
      const subject = new Subject<Experiments[K]>();
      const onNewExperimentValue = (newValue: Experiments[K]) => {
        subject.next(newValue);
      };
      ldClient.current?.on(`change:${key}`, onNewExperimentValue);
      return subject.pipe(
        finalize(() => {
          ldClient.current?.off(`change:${key}`, onNewExperimentValue);
        })
      );
    },
  };

  return <ExperimentProvider value={experimentService}>{children}</ExperimentProvider>;
};

export const LDExperimentServiceProvider: React.FC = ({ children }) => {
  const { launchdarkly: launchdarklyKey } = useConfig();

  return !launchdarklyKey ? (
    <>{children}</>
  ) : (
    <LDInitializationWrapper apiKey={launchdarklyKey}>{children}</LDInitializationWrapper>
  );
};
