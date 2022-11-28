import type { Auth } from "firebase/auth";

import * as React from "react";

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

export const AuthProvider = getSdkProvider<Auth>(AuthSdkContext);
export const useAuth = (): Auth => useSdk<Auth>(AuthSdkContext);
