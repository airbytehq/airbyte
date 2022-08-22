import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";

import { Button, LoadingPage, MainPageWithScroll, PageTitle } from "components";
import { EmptyResourceListView } from "components/EmptyResourceListView";
import HeadTitle from "components/HeadTitle";

import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useConnectionList } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";

import { RoutePaths } from "../../../routePaths";
import ConnectionsTable from "./components/ConnectionsTable";

const AllConnectionsPage: React.FC = () => {
  const { push } = useRouter();

  const { connections } = useConnectionList();
  const allowCreateConnection = useFeature(FeatureItem.AllowCreateConnection);

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
                <Button onClick={onCreateClick} disabled={!allowCreateConnection}>
                  <FormattedMessage id="connection.newConnection" />
                </Button>
              }
            />
          }
        >
          <ConnectionsTable connections={connections} />
        </MainPageWithScroll>
      ) : (
        <EmptyResourceListView
          resourceType="connections"
          onCreateClick={onCreateClick}
          disableCreateButton={!allowCreateConnection}
        />
      )}
    </Suspense>
  );
};

export default AllConnectionsPage;
