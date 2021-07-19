import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource } from "rest-hooks";

import { Button } from "components";
import { Routes } from "../../../routes";
import PageTitle from "components/PageTitle";
import useRouter from "components/hooks/useRouterHook";
import DestinationsTable from "./components/DestinationsTable";
import ContentCard from "components/ContentCard";
import EmptyResource from "components/EmptyResourceBlock";
import DestinationResource from "core/resources/Destination";
import HeadTitle from "components/HeadTitle";
import useWorkspace from "components/hooks/services/useWorkspace";

const Content = styled(ContentCard)`
  margin: 0 32px 0 27px;
`;

const AllDestinationsPage: React.FC = () => {
  const { push } = useRouter();
  const { workspace } = useWorkspace();
  const { destinations } = useResource(DestinationResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });

  const onCreateDestination = () =>
    push(`${Routes.Destination}${Routes.DestinationNew}`);

  return (
    <>
      <HeadTitle titles={[{ id: "admin.destinations" }]} />
      <PageTitle
        title={<FormattedMessage id="admin.destinations" />}
        endComponent={
          <Button onClick={onCreateDestination} data-id="new-destination">
            <FormattedMessage id="destination.newDestination" />
          </Button>
        }
      />
      {destinations.length ? (
        <DestinationsTable destinations={destinations} />
      ) : (
        <Content>
          <EmptyResource
            text={<FormattedMessage id="destinations.noDestinations" />}
          />
        </Content>
      )}
    </>
  );
};

export default AllDestinationsPage;
