import React from "react";
import { getAuth } from "firebase/auth";
import { useConfig } from "packages/cloud/services/config";

import {
  FirebaseAppProvider,
  useFirebaseApp,
  AuthProvider,
} from "packages/firebaseReact";

const FirebaseAppSdksProvider: React.FC = ({ children }) => {
  const firebaseApp = useFirebaseApp();
  const auth = getAuth(firebaseApp);

  return <AuthProvider sdk={auth}>{children}</AuthProvider>;
};

/**
 * This Provider is responsible for injecting firebase app
 * based on airbyte app config and also injecting all required firebase sdks
 */
const FirebaseSdkProvider: React.FC = ({ children }) => {
  const config = useConfig();

  return (
    <FirebaseAppProvider firebaseConfig={config.firebase}>
      <FirebaseAppSdksProvider>{children}</FirebaseAppSdksProvider>
    </FirebaseAppProvider>
  );
};

export { FirebaseSdkProvider };
