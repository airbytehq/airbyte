import React, { Suspense, useMemo } from "react";
import { Outlet, useLocation, useParams } from "react-router-dom";

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
import { ConnectionRoutePaths } from "../types";

const ConnectionHeadTitle: React.FC = () => {
  const { connection } = useConnectionEditService();

  return (
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
  );
};

export const ConnectionPage: React.FC = () => {
  const { connectionId = "" } = useParams<{
    connectionId: string;
  }>();
  const location = useLocation();
  const isReplicationPage = useMemo(
    () => location.pathname.includes(`/${ConnectionRoutePaths.Replication}`),
    [location.pathname]
  );

  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM);

  return (
    <ConnectionEditServiceProvider connectionId={connectionId}>
      <ResourceNotFoundErrorBoundary errorComponent={<StartOverErrorView />}>
        <MainPageWithScroll
          headTitle={<ConnectionHeadTitle />}
          pageTitle={<ConnectionPageTitle />}
          noBottomPadding={isReplicationPage}
        >
          <Suspense fallback={<LoadingPage />}>
            <Outlet />
          </Suspense>
        </MainPageWithScroll>
      </ResourceNotFoundErrorBoundary>
    </ConnectionEditServiceProvider>
  );
};
