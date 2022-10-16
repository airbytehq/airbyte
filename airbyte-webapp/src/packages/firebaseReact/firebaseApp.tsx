/**
 * Impressed by https://github.com/FirebaseExtended/reactfire
 */
import type { FirebaseApp, FirebaseOptions } from "firebase/app";

import { getApps, initializeApp, registerVersion } from "firebase/app";
import * as React from "react";

import { equal } from "utils/objects";

const DEFAULT_APP_NAME = "[DEFAULT]";

const FirebaseAppContext = React.createContext<FirebaseApp | undefined>(undefined);
const SuspenseEnabledContext = React.createContext<boolean>(false);

interface FirebaseAppProviderProps {
  firebaseApp?: FirebaseApp;
  firebaseConfig?: FirebaseOptions;
  appName?: string;
  suspense?: boolean;
}

export const FirebaseAppProvider = (props: React.PropsWithChildren<FirebaseAppProviderProps>): JSX.Element => {
  const { firebaseConfig, appName, suspense } = props;

  const firebaseApp: FirebaseApp = React.useMemo(() => {
    if (props.firebaseApp) {
      return props.firebaseApp;
    }

    const existingApp = getApps().find((app) => app.name === (appName || DEFAULT_APP_NAME));
    if (existingApp) {
      if (firebaseConfig && equal(existingApp.options, firebaseConfig)) {
        return existingApp;
      }
      throw new Error(
        `Does not match the options already provided to the ${
          appName || "default"
        } firebase app instance, give this new instance a different appName.`
      );
    } else {
      if (!firebaseConfig) {
        throw new Error("No firebaseConfig provided");
      }

      const reactVersion = React.version || "unknown";
      registerVersion("react", reactVersion);
      return initializeApp(firebaseConfig, appName);
    }
  }, [props.firebaseApp, firebaseConfig, appName]);

  return (
    <FirebaseAppContext.Provider value={firebaseApp}>
      <SuspenseEnabledContext.Provider value={suspense ?? false} {...props} />
    </FirebaseAppContext.Provider>
  );
};

export function useFirebaseApp(): FirebaseApp {
  const firebaseApp = React.useContext(FirebaseAppContext);
  if (!firebaseApp) {
    throw new Error("Cannot call useFirebaseApp unless your component is within a FirebaseAppProvider");
  }

  return firebaseApp;
}
