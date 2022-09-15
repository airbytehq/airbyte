import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";

import { Button, LoadingPage, MainPageWithScroll, PageTitle } from "components";
import { EmptyResourceListView } from "components/EmptyResourceListView";
import HeadTitle from "components/HeadTitle";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useConnectionList } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";

import { RoutePaths } from "../../../routePaths";
import ConnectionsTable from "./components/ConnectionsTable";

const AllConnectionsPage: React.FC = () => {
  const { push } = useRouter();

  useTrackPage(PageTrackingCodes.CONNECTIONS_LIST);
  const { connections } = useConnectionList();

  const onCreateClick = () => push(`${RoutePaths.ConnectionNew}`);

  return (
    <Suspense fallback={<LoadingPage />}>
      {connections.length ? (
        <MainPageWithScroll
          headTitle={<HeadTitle titles={[{ id: "sidebar.connections" }]} />}
          pageTitle={
            <PageTitle
              title={<FormattedMessage id="sidebar.connections" />}
              endComponent={
                <Button onClick={onCreateClick}>
                  <FormattedMessage id="connection.newConnection" />
                </Button>
              }
            />
          }
        >
          <ConnectionsTable connections={connections} />
        </MainPageWithScroll>
      ) : (
        <EmptyResourceListView resourceType="connections" onCreateClick={onCreateClick} />
      )}
    </Suspense>
  );
};

export default AllConnectionsPage;
