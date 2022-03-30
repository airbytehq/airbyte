import React, { useMemo, useRef } from "react";

import { useAuth } from "packages/firebaseReact";

import { ServicesProvider, useInjectServices } from "core/servicesProvider";
import { FirebaseSdkProvider } from "./FirebaseSdkProvider";
import { RequestAuthMiddleware } from "packages/cloud/lib/auth/RequestAuthMiddleware";
import { useConfig } from "./config";
import { UserService } from "packages/cloud/lib/domain/users";
import { LoadingPage } from "components";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

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
  const { cloudApiUrl } = useConfig();

  const user = useRef(auth.currentUser);
  user.current = auth.currentUser;

  const inject = useMemo(() => {
    const middlewares = [
      RequestAuthMiddleware({
        getValue() {
          return user.current?.getIdToken() ?? "";
        },
      }),
    ];

    const ctx = {
      UserService: new UserService(cloudApiUrl, middlewares),
      DefaultRequestMiddlewares: middlewares,
    };

    return ctx;
  }, [cloudApiUrl]);

  useInjectServices(inject);

  const registeredMiddlewares = useDefaultRequestMiddlewares();

  return <>{registeredMiddlewares ? <>{children}</> : <LoadingPage />}</>;
});

export { AppServicesProvider };
