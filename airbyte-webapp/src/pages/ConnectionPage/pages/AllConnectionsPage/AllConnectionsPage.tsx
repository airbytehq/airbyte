import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";

import { Button, LoadingPage, MainPageWithScroll, PageTitle } from "components";
import HeadTitle from "components/HeadTitle";
import Placeholder, { ResourceTypes } from "components/Placeholder";

import { FeatureItem, useFeatureService } from "hooks/services/Feature";
import { useConnectionList } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";

import { listConnectionsForWorkspace } from "../../../../core/request/GeneratedApi";
import { useCurrentWorkspace } from "../../../../services/workspaces/WorkspacesService";
import { RoutePaths } from "../../../routePaths";
import ConnectionsTable from "./components/ConnectionsTable";

const AllConnectionsPage: React.FC = () => {
  const { push } = useRouter();

  const workspace = useCurrentWorkspace();
  const { connections } = useConnectionList();
  // const conns = useListConnectionsForWorkspace();
  const lConns = listConnectionsForWorkspace({ workspaceId: workspace.workspaceId });
  console.log(lConns);
  const { hasFeature } = useFeatureService();
  const allowCreateConnection = hasFeature(FeatureItem.AllowCreateConnection);

  const onClick = () => push(`${RoutePaths.ConnectionNew}`);

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "sidebar.connections" }]} />}
      pageTitle={
        <PageTitle
          title={<FormattedMessage id="sidebar.connections" />}
          endComponent={
            <Button onClick={onClick} disabled={!allowCreateConnection}>
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
