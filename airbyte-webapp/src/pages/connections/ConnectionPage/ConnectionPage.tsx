import React, { Suspense } from "react";
import { Outlet, useParams } from "react-router-dom";

import { LoadingPage, MainPageWithScroll } from "components";
import { HeadTitle } from "components/common/HeadTitle";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import {
  ConnectionEditServiceProvider,
  useConnectionEditService,
} from "hooks/services/ConnectionEdit/ConnectionEditService";
import { ResourceNotFoundErrorBoundary } from "views/common/ResorceNotFoundErrorBoundary";
import { StartOverErrorView } from "views/common/StartOverErrorView";

import { ConnectionPageTitle } from "./ConnectionPageTitle";

export const ConnectionPageInner: React.FC = () => {
  const { connection } = useConnectionEditService();

  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM);

  return (
    <MainPageWithScroll
      headTitle={
        <HeadTitle
          titles={[
            { id: "sidebar.connections" },
            {
              id: "connection.fromTo",
              values: {
                source: connection.source.name,
                destination: connection.destination.name,
              },
            },
          ]}
        />
      }
      pageTitle={<ConnectionPageTitle />}
    >
      <Suspense fallback={<LoadingPage />}>
        <Outlet />
      </Suspense>
    </MainPageWithScroll>
  );
};

export const ConnectionPage = () => {
  const params = useParams<{
    connectionId: string;
  }>();
  const connectionId = params.connectionId || "";

  return (
    <ConnectionEditServiceProvider connectionId={connectionId}>
      <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
        <ConnectionPageInner />
      </ResourceNotFoundErrorBoundary>
    </ConnectionEditServiceProvider>
  );
};
