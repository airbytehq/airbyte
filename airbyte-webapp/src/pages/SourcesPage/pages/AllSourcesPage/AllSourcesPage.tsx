import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource, useSubscription } from "rest-hooks";

import Button from "../../../../components/Button";
import { Routes } from "../../../routes";
import PageTitle from "../../../../components/PageTitle";
import useRouter from "../../../../components/hooks/useRouterHook";
import SourcesTable from "./components/SourcesTable";
import ConnectionResource from "../../../../core/resources/Connection";
import config from "../../../../config";
import ContentCard from "../../../../components/ContentCard";
import EmptyResource from "../../components/EmptyResource";

const Content = styled(ContentCard)`
  margin: 0 32px 0 27px;
`;

const AllSourcesPage: React.FC = () => {
  const { push } = useRouter();
  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });
  useSubscription(ConnectionResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });

  const onCreateSource = () => push(`${Routes.Source}${Routes.SourceNew}`);
  return (
    <>
      <PageTitle
        title={<FormattedMessage id="sidebar.sources" />}
        endComponent={
          <Button onClick={onCreateSource}>
            <FormattedMessage id="sources.newSource" />
          </Button>
        }
      />
      {connections.length ? (
        <SourcesTable connections={connections} />
      ) : (
        <Content>
          <EmptyResource text={<FormattedMessage id="sources.noSources" />} />
        </Content>
      )}
    </>
  );
};

export default AllSourcesPage;
