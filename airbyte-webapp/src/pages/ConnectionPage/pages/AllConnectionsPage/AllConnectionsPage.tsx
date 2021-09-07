import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import { Button, MainPageWithScroll, PageTitle, LoadingPage } from "components";
import ConnectionResource from "core/resources/Connection";
import ConnectionsTable from "./components/ConnectionsTable";
import { Routes } from "pages/routes";
import useRouter from "hooks/useRouter";
import HeadTitle from "components/HeadTitle";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import useWorkspace from "hooks/services/useWorkspace";

const AllConnectionsPage: React.FC = () => {
  const { push } = useRouter();
  const { workspace } = useWorkspace();
  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });

  const onClick = () => push(`${Routes.Connections}${Routes.ConnectionNew}`);

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "sidebar.connections" }]} />}
      pageTitle={
        <PageTitle
          title={<FormattedMessage id="sidebar.connections" />}
          endComponent={
            <Button onClick={onClick}>
              <FormattedMessage id="connection.newConnection" />
            </Button>
          }
        />
      }
    >
      <Suspense fallback={<LoadingPage />}>
        {connections.length ? (
          <ConnectionsTable connections={connections} />
        ) : (
          <Placeholder resource={ResourceTypes.Connections} />
        )}
      </Suspense>
    </MainPageWithScroll>
  );
};

export default AllConnectionsPage;
