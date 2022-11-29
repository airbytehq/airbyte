import * as LDClient from "launchdarkly-js-client-sdk";
import { useEffect, useRef, useState } from "react";
import { useIntl } from "react-intl";
import { useEffectOnce } from "react-use";
import { finalize, Subject } from "rxjs";

import { LoadingPage } from "components";

import { useConfig } from "config";
import { useI18nContext } from "core/i18n";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useAppMonitoringService, AppActionCodes } from "hooks/services/AppMonitoringService";
import { ExperimentProvider, ExperimentService } from "hooks/services/Experiment";
import type { Experiments } from "hooks/services/Experiment/experiments";
import { FeatureSet, FeatureItem, useFeatureService } from "hooks/services/Feature";
import { User } from "packages/cloud/lib/domain/users";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { rejectAfter } from "utils/promises";

/**
 * This service hardcodes two conventions about the format of the LaunchDarkly feature
 * flags we use to override feature settings:
 * 1) each feature flag's key (a unique string which is used as the flag's field name in
 *    LaunchDarkly's JSON payloads) is a string satisfying the LDFeatureName type.
 * 2) for each feature flag, LaunchDarkly will return a JSON blob satisfying the
 *    LDFeatureToggle type.
 *
 * The primary benefit of programmatically requiring a specific prefix is to provide a
 * reliable search term which can be used in LaunchDarkly to filter the list of feature
 * flags to all of, and only, the ones which can dynamically toggle features in the UI.
 *
 * LDFeatureToggle objects can take three forms, representing the three possible decision
 * states LaunchDarkly can provide for a user/feature pair:
 * |--------------------------+-----------------------------------------------|
 * | `{}`                     | use the application's default feature setting |
 * | `{ "enabled": true }`    | enable the feature                            |
 * | `{ "enabled": false }`   | disable the feature                           |
 * |--------------------------+-----------------------------------------------|
 */
const FEATURE_FLAG_PREFIX = "featureService";
type LDFeatureName = `${typeof FEATURE_FLAG_PREFIX}.${FeatureItem}`;
interface LDFeatureToggle {
  enabled?: boolean;
}
type LDFeatureFlagResponse = Record<LDFeatureName, LDFeatureToggle>;
type LDInitState = "initializing" | "failed" | "initialized";

/**
 * The maximum time in milliseconds we'll wait for LaunchDarkly to finish initialization,
 * before running disabling it.
 */
const INITIALIZATION_TIMEOUT = 5000;

function mapUserToLDUser(user: User | null, locale: string): LDClient.LDUser {
  return user
    ? {
        key: user.userId,
        email: user.email,
        name: user.name,
        custom: { intercomHash: user.intercomHash, locale },
        anonymous: false,
      }
    : {
        anonymous: true,
        custom: { locale },
      };
}

const LDInitializationWrapper: React.FC<React.PropsWithChildren<{ apiKey: string }>> = ({ children, apiKey }) => {
  const { setFeatureOverwrites } = useFeatureService();
  const ldClient = useRef<LDClient.LDClient>();
  const [state, setState] = useState<LDInitState>("initializing");
  const { user } = useAuthService();
  const analyticsService = useAnalyticsService();
  const { locale } = useIntl();
  const { setMessageOverwrite } = useI18nContext();
  const { trackAction } = useAppMonitoringService();

  /**
   * This function checks for all experiments to find the ones beginning with "i18n_{locale}_"
   * and treats them as message overwrites for our bundled messages. Empty messages will be treated as not overwritten.
   */
  const updateI18nMessages = () => {
    const prefix = `i18n_`;
    const messageOverwrites = Object.entries(ldClient.current?.allFlags() ?? {})
      // Only filter experiments beginning with the prefix and having an actual non-empty string value set
      .filter(([id, value]) => id.startsWith(prefix) && !!value && typeof value === "string")
      // Slice away the prefix of the key, to only keep the actual i18n id as a key
      .map(([id, msg]) => [id.slice(prefix.length), msg]);
    // Use those messages as overwrites in the i18nContext
    setMessageOverwrite(Object.fromEntries(messageOverwrites));
  };

  /**
   * Update the feature overwrites based on the LaunchDarkly value.
   * The feature flag variants which do not include a JSON `enabled` field are filtered
   * out; then, each feature corresponding to one of the remaining feature flag overwrites
   * is either enabled or disabled for the current user based on the boolean value of its
   * overwrite's `enabled` field.
   */
  const updateFeatureOverwrites = () => {
    const allFlags = (ldClient.current?.allFlags() ?? {}) as LDFeatureFlagResponse;
    const featureSet: FeatureSet = Object.fromEntries(
      Object.entries(allFlags)
        .filter(([flagName]) => flagName.startsWith(FEATURE_FLAG_PREFIX))
        .map(([flagName, { enabled }]) => [flagName.replace(`${FEATURE_FLAG_PREFIX}.`, ""), enabled])
        .filter(([_, enabled]) => typeof enabled !== "undefined")
    );

    setFeatureOverwrites(featureSet);
  };

  if (!ldClient.current) {
    ldClient.current = LDClient.initialize(apiKey, mapUserToLDUser(user, locale));
    // Wait for either LaunchDarkly to initialize or a specific timeout to pass first
    Promise.race([
      ldClient.current.waitForInitialization(),
      rejectAfter(INITIALIZATION_TIMEOUT, AppActionCodes.LD_LOAD_TIMEOUT),
    ])
      .then(() => {
        // The LaunchDarkly promise resolved before the timeout, so we're good to use LD.
        setState("initialized");
        // Make sure enabled experiments are added to each analytics event
        analyticsService.setContext({ experiments: JSON.stringify(ldClient.current?.allFlags()) });
        // Check for overwritten i18n messages
        updateI18nMessages();
        updateFeatureOverwrites();
      })
      .catch((reason) => {
        // If the promise fails, either because LaunchDarkly service fails to initialize, or
        // our timeout promise resolves first, we're going to show an error and assume the service
        // failed to initialize, i.e. we'll run without it.
        console.warn(`Failed to initialize LaunchDarkly service with reason: ${String(reason)}`);
        if (reason === AppActionCodes.LD_LOAD_TIMEOUT) {
          trackAction(AppActionCodes.LD_LOAD_TIMEOUT);
        }
        setState("failed");
      });
  }

  useEffectOnce(() => {
    const onFeatureFlagsChanged = () => {
      // Update analytics context whenever a flag changes
      analyticsService.setContext({ experiments: JSON.stringify(ldClient.current?.allFlags()) });
      // Check for overwritten i18n messages
      updateI18nMessages();
      updateFeatureOverwrites();
    };
    ldClient.current?.on("change", onFeatureFlagsChanged);
    return () => ldClient.current?.off("change", onFeatureFlagsChanged);
  });

  // Whenever the user should change (e.g. login/logout) we need to reidentify the changes with the LD client
  useEffect(() => {
    ldClient.current?.identify(mapUserToLDUser(user, locale));
  }, [locale, user]);

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

export const LDExperimentServiceProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { launchDarkly: launchdarklyKey } = useConfig();

  return !launchdarklyKey ? (
    <>{children}</>
  ) : (
    <LDInitializationWrapper apiKey={launchdarklyKey}>{children}</LDInitializationWrapper>
  );
};
