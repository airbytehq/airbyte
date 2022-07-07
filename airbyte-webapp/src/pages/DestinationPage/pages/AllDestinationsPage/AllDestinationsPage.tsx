import React from "react";
import { FormattedMessage } from "react-intl";

import { Button, MainPageWithScroll } from "components";
import { EmptyResourceListView } from "components/EmptyResourceListView";
import HeadTitle from "components/HeadTitle";
import PageTitle from "components/PageTitle";

import { useDestinationList } from "hooks/services/useDestinationHook";
import useRouter from "hooks/useRouter";

import { RoutePaths } from "../../../routePaths";
import DestinationsTable from "./components/DestinationsTable";

const AllDestinationsPage: React.FC = () => {
  const { push } = useRouter();
  const { destinations } = useDestinationList();

  const onCreateDestination = () => push(`${RoutePaths.DestinationNew}`);

  return destinations.length ? (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "admin.destinations" }]} />}
      pageTitle={
        <PageTitle
          title={<FormattedMessage id="admin.destinations" />}
          endComponent={
            <Button onClick={onCreateDestination} data-id="new-destination">
              <FormattedMessage id="destinations.newDestination" />
            </Button>
          }
        />
      }
    >
      <DestinationsTable destinations={destinations} />
    </MainPageWithScroll>
  ) : (
    <EmptyResourceListView resourceType="destinations" onCreateClick={onCreateDestination} />
  );
};

export default AllDestinationsPage;
