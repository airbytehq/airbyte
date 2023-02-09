import React, { useMemo } from "react";

import { LoadingPage } from "components";

import { MissingConfigError, useConfig } from "config";
import { ApiServices } from "core/ApiServices";
import { RequestMiddleware } from "core/request/RequestMiddleware";
import { ServicesProvider, useGetService, useInjectServices } from "core/servicesProvider";
import { RequestAuthMiddleware } from "packages/cloud/lib/auth/RequestAuthMiddleware";
import { UserService } from "packages/cloud/lib/domain/users";
import { useAuth } from "packages/firebaseReact";

import { FirebaseSdkProvider } from "./FirebaseSdkProvider";

/**
 * This Provider is main services entrypoint
 * It initializes all required services for app to work
 * and also adds all overrides of hooks/services
 */
const AppServicesProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  return (
    <ServicesProvider>
      <FirebaseSdkProvider>
        <ServiceOverrides>{children}</ServiceOverrides>
      </FirebaseSdkProvider>
    </ServicesProvider>
  );
};

const ServiceOverrides: React.FC<React.PropsWithChildren<unknown>> = React.memo(({ children }) => {
  const auth = useAuth();

  const middlewares: RequestMiddleware[] = useMemo(
    () => [
      RequestAuthMiddleware({
        getValue() {
          return auth.currentUser?.getIdToken() ?? "";
        },
      }),
    ],
    [auth]
  );

  const { cloudApiUrl } = useConfig();

  if (!cloudApiUrl) {
    throw new MissingConfigError("Missing required configuration cloudApiUrl");
  }

  const inject = useMemo(
    () => ({
      UserService: new UserService(cloudApiUrl, middlewares),
      DefaultRequestMiddlewares: middlewares,
    }),
    [cloudApiUrl, middlewares]
  );

  useInjectServices(inject);

  const registeredMiddlewares = useGetService("DefaultRequestMiddlewares");

  return <ApiServices>{registeredMiddlewares ? <>{children}</> : <LoadingPage />}</ApiServices>;
});

export { AppServicesProvider };
