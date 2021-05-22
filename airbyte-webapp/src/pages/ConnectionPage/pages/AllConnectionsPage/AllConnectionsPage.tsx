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
import config from "config";
import ConnectionsTable from "./components/ConnectionsTable";
import { Routes } from "pages/routes";
import useRouter from "components/hooks/useRouterHook";
import EmptyResource from "components/EmptyResourceBlock";
import HeadTitle from "components/HeadTitle";

const Content = styled(ContentCard)`
  margin: 0 32px 0 27px;
`;

const AllConnectionsPage: React.FC = () => {
  const { push } = useRouter();

  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: config.ui.workspaceId,
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
