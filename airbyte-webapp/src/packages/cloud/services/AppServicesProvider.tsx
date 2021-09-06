import React, { useMemo } from "react";
import { useResource } from "rest-hooks";

import { useAuth } from "packages/firebaseReact";

import {
  ServicesProvider,
  useGetService,
  useInjectServices,
} from "core/servicesProvider";
import { useApiServices } from "core/defaultServices";
import { ConfigProvider } from "./ConfigProvider";
import { FirebaseSdkProvider } from "./FirebaseSdkProvider";

import { useWorkspaceService } from "./workspaces/WorkspacesService";
import { useAuthService } from "./auth/AuthService";
import WorkspaceResource, { Workspace } from "core/resources/Workspace";
import { RequestAuthMiddleware } from "packages/cloud/lib/auth/RequestAuthMiddleware";
import { useConfig } from "./config";
import { UserService } from "packages/cloud/lib/domain/users";
import { RequestMiddleware } from "core/request/RequestMiddleware";
import { LoadingPage } from "components";

export const useCustomerIdProvider = (): string => {
  const { user } = useAuthService();
  return user?.userId ?? "";
};

export const useCurrentWorkspaceProvider = (): Workspace => {
  const { currentWorkspaceId } = useWorkspaceService();
  const workspace = useResource(WorkspaceResource.detailShape(), {
    workspaceId: currentWorkspaceId || null,
  });

  return workspace;
};

/**
 * This Provider is main services entrypoint
 * It initializes all required services for app to work
 * and also adds all overrides of hooks/services
 */
const AppServicesProvider: React.FC = ({ children }) => {
  const services = useMemo(
    () => ({
      currentWorkspaceProvider: useCurrentWorkspaceProvider,
      useCustomerIdProvider: useCustomerIdProvider,
    }),
    []
  );
  return (
    <ServicesProvider inject={services}>
      <ConfigProvider>
        <FirebaseSdkProvider>
          <ServiceOverrides>{children}</ServiceOverrides>
        </FirebaseSdkProvider>
      </ConfigProvider>
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
  useApiServices();

  const registeredMiddlewares = useGetService("DefaultRequestMiddlewares");

  return registeredMiddlewares ? <>{children}</> : <LoadingPage />;
});

export { AppServicesProvider };
