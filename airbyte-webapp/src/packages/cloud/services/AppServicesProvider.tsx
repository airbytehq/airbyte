import React, { useMemo } from "react";

import { useAuth } from "packages/firebaseReact";

import {
  ServicesProvider,
  useGetService,
  useInjectServices,
} from "core/servicesProvider";
import { ApiServices } from "core/ApiServices";
import { FirebaseSdkProvider } from "./FirebaseSdkProvider";
import { RequestAuthMiddleware } from "packages/cloud/lib/auth/RequestAuthMiddleware";
import { useConfig } from "./config";
import { UserService } from "packages/cloud/lib/domain/users";
import { RequestMiddleware } from "core/request/RequestMiddleware";
import { LoadingPage } from "components";

/**
 * This Provider is main services entrypoint
 * It initializes all required services for app to work
 * and also adds all overrides of hooks/services
 */
const AppServicesProvider: React.FC = ({ children }) => {
  return (
    <ServicesProvider>
      <FirebaseSdkProvider>
        <ServiceOverrides>{children}</ServiceOverrides>
      </FirebaseSdkProvider>
    </ServicesProvider>
  );
};

const ServiceOverrides: React.FC = React.memo(({ children }) => {
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

  const inject = useMemo(
    () => ({
      UserService: new UserService(cloudApiUrl, middlewares),
      DefaultRequestMiddlewares: middlewares,
    }),
    [cloudApiUrl, middlewares]
  );

  useInjectServices(inject);

  const registeredMiddlewares = useGetService("DefaultRequestMiddlewares");

  return (
    <ApiServices>
      {registeredMiddlewares ? <>{children}</> : <LoadingPage />}
    </ApiServices>
  );
});

export { AppServicesProvider };
