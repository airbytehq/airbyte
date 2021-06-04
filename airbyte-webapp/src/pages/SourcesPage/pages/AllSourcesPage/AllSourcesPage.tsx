import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource } from "rest-hooks";

import { Button } from "components";
import { Routes } from "../../../routes";
import PageTitle from "components/PageTitle";
import useRouter from "components/hooks/useRouterHook";
import SourcesTable from "./components/SourcesTable";
import config from "config";
import ContentCard from "components/ContentCard";
import EmptyResource from "components/EmptyResourceBlock";
import SourceResource from "core/resources/Source";
import HeadTitle from "components/HeadTitle";

const Content = styled(ContentCard)`
  margin: 0 32px 0 27px;
`;

const AllSourcesPage: React.FC = () => {
  const { push } = useRouter();

  const { sources } = useResource(SourceResource.listShape(), {
    workspaceId: config.ui.workspaceId,
  });

  const onCreateSource = () => push(`${Routes.Source}${Routes.SourceNew}`);
  return (
    <>
      <HeadTitle titles={[{ id: "admin.sources" }]} />
      <PageTitle
        title={<FormattedMessage id="sidebar.sources" />}
        endComponent={
          <Button onClick={onCreateSource} data-id="new-source">
            <FormattedMessage id="sources.newSource" />
          </Button>
        }
      />
      {sources.length ? (
        <SourcesTable sources={sources} />
      ) : (
        <Content>
          <EmptyResource text={<FormattedMessage id="sources.noSources" />} />
        </Content>
      )}
    </>
  );
};

export default AllSourcesPage;
