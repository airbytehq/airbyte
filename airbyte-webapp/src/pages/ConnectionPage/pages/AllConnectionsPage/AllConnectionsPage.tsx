import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";
import styled from "styled-components";

import {
  Button,
  MainPageWithScroll,
  PageTitle,
  LoadingPage,
  ContentCard,
} from "components";
import ConnectionResource from "core/resources/Connection";
import ConnectionsTable from "./components/ConnectionsTable";
import { Routes } from "pages/routes";
import useRouter from "components/hooks/useRouterHook";
import EmptyResource from "components/EmptyResourceBlock";
import HeadTitle from "components/HeadTitle";
import useWorkspace from "components/hooks/services/useWorkspace";

const Content = styled(ContentCard)`
  margin: 0 32px 0 27px;
`;

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
          <Content>
            <EmptyResource
              text={<FormattedMessage id="connection.noConnections" />}
            />
          </Content>
        )}
      </Suspense>
    </MainPageWithScroll>
  );
};

export default AllConnectionsPage;
