import { getAuth, connectAuthEmulator } from "firebase/auth";
import React from "react";

import { useConfig } from "config";
import { FirebaseAppProvider, useFirebaseApp, AuthProvider } from "packages/firebaseReact";

const FirebaseAppSdksProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const config = useConfig();
  const firebaseApp = useFirebaseApp();
  const auth = getAuth(firebaseApp);
  if (config.firebase.authEmulatorHost) {
    connectAuthEmulator(auth, config.firebase.authEmulatorHost);
  }

  return <AuthProvider sdk={auth}>{children}</AuthProvider>;
};

/**
 * This Provider is responsible for injecting firebase app
 * based on airbyte app config and also injecting all required firebase sdks
 */
const FirebaseSdkProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const config = useConfig();

  return (
    <FirebaseAppProvider firebaseConfig={config.firebase}>
      <FirebaseAppSdksProvider>{children}</FirebaseAppSdksProvider>
    </FirebaseAppProvider>
  );
};

export { FirebaseSdkProvider };
