import type { Auth } from "firebase/auth";

import { FirebaseApp } from "firebase/app";
import * as React from "react";
import { useAsync } from "react-use";
import { AsyncState } from "react-use/lib/useAsyncFn";

import { useFirebaseApp } from "./firebaseApp";

const AuthSdkContext = React.createContext<Auth | undefined>(undefined);

type FirebaseSdks = Auth;

function getSdkProvider<Sdk extends FirebaseSdks>(SdkContext: React.Context<Sdk | undefined>) {
  return (props: React.PropsWithChildren<{ sdk: Sdk }>) => {
    if (!props.sdk) {
      throw new Error("no sdk provided");
    }

    const contextualAppName = useFirebaseApp().name;
    const sdkAppName = props?.sdk?.app?.name;
    if (sdkAppName !== contextualAppName) {
      throw new Error("sdk was initialized with a different firebase app");
    }

    return <SdkContext.Provider value={props.sdk} {...props} />;
  };
}

function useSdk<Sdk extends FirebaseSdks>(SdkContext: React.Context<Sdk | undefined>): Sdk {
  const sdk = React.useContext(SdkContext);

  if (!sdk) {
    throw new Error("SDK not found. useSdk must be called from within a provider");
  }

  return sdk;
}

function useInitSdk<Sdk extends FirebaseSdks>(
  sdkName: string,
  SdkContext: React.Context<Sdk | undefined>,
  sdkInitializer: (firebaseApp: FirebaseApp) => Promise<Sdk>
) {
  const firebaseApp = useFirebaseApp();

  // Some initialization functions (like Firestore's `enableIndexedDbPersistence`)
  // can only be called before anything else. So if an sdk is already available in context,
  // it isn't safe to call initialization functions again.
  if (React.useContext(SdkContext)) {
    throw new Error(`Cannot initialize SDK ${sdkName} because it already exists in Context`);
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const initializeSdk = React.useMemo(() => sdkInitializer(firebaseApp), [firebaseApp]);

  return useAsync(() => initializeSdk);
}

export const AuthProvider = getSdkProvider<Auth>(AuthSdkContext);
export const useAuth = (): Auth => useSdk<Auth>(AuthSdkContext);

type InitSdkHook<Sdk extends FirebaseSdks> = (
  initializer: (firebaseApp: FirebaseApp) => Promise<Sdk>
) => AsyncState<Sdk>;

export const useInitAuth: InitSdkHook<Auth> = (initializer) => useInitSdk<Auth>("auth", AuthSdkContext, initializer);
