import * as LDClient from "launchdarkly-js-client-sdk";
import { useEffect, useRef, useState } from "react";
import { useEffectOnce } from "react-use";
import { finalize, Subject } from "rxjs";

import { LoadingPage } from "components";

import { useConfig } from "config";
import { useAnalytics } from "hooks/services/Analytics";
import { ExperimentProvider, ExperimentService } from "hooks/services/Experiment";
import type { Experiments } from "hooks/services/Experiment/experiments";
import { User } from "packages/cloud/lib/domain/users";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { rejectAfter } from "utils/promises";

/**
 * The maximum time in milliseconds we'll wait for LaunchDarkly to finish initialization,
 * before running disabling it.
 */
const INITIALIZATION_TIMEOUT = 1500;

type LDInitState = "initializing" | "failed" | "initialized";

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
  const { addContextProps: addAnalyticsContext } = useAnalytics();

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
        // Make sure enabled experiments are added to each analytics event
        addAnalyticsContext({ experiments: ldClient.current?.allFlags() });
      })
      .catch((reason) => {
        // If the promise fails, either because LaunchDarkly service fails to initialize, or
        // our timeout promise resolves first, we're going to show an error and assume the service
        // failed to initialize, i.e. we'll run without it.
        console.warn(`Failed to initialize LaunchDarkly service with reason: ${String(reason)}`);
        setState("failed");
      });
  }

  useEffectOnce(() => {
    const onFeatureFlagsChanged = () => {
      // Update analytics context whenever a flag changes
      addAnalyticsContext({ experiments: ldClient.current?.allFlags() });
    };
    ldClient.current?.on("change", onFeatureFlagsChanged);
    return () => ldClient.current?.off("change", onFeatureFlagsChanged);
  });

  // Whenever the user should change (e.g. login/logout) we need to reidentify the changes with the LD client
  useEffect(() => {
    ldClient.current?.identify(mapUserToLDUser(user));
  }, [user]);

  // Show the loading page while we're still waiting for the initial set of feature flags (or them to time out)
  if (state === "initializing") {
    return <LoadingPage />;
  }

  // Render without an experimentation service in case we failed loading the service, in which case all usages of
  // useExperiment will return the defaultValue passed in.
  if (state === "failed") {
    return <>{children}</>;
  }

  const experimentService: ExperimentService = {
    getExperiment(key, defaultValue) {
      // Return the current value of a feature flag from the LD client
      return ldClient.current?.variation(key, defaultValue);
    },
    getExperimentChanges$<K extends keyof Experiments>(key: K) {
      // To retrieve changes from the LD client, we're subscribing to changes
      // for that specific key (emitted via the change:key event) and emit that
      // on our observable.
      const subject = new Subject<Experiments[K]>();
      const onNewExperimentValue = (newValue: Experiments[K]) => {
        subject.next(newValue);
      };
      ldClient.current?.on(`change:${key}`, onNewExperimentValue);
      return subject.pipe(
        finalize(() => {
          // Whenever the last subscriber disconnects (or the observable would complete, which
          // we never do for this observable), make sure to unregister our event listener again
          ldClient.current?.off(`change:${key}`, onNewExperimentValue);
        })
      );
    },
  };

  return <ExperimentProvider value={experimentService}>{children}</ExperimentProvider>;
};

export const LDExperimentServiceProvider: React.FC = ({ children }) => {
  const { launchDarkly: launchdarklyKey } = useConfig();

  return !launchdarklyKey ? (
    <>{children}</>
  ) : (
    <LDInitializationWrapper apiKey={launchdarklyKey}>{children}</LDInitializationWrapper>
  );
};
