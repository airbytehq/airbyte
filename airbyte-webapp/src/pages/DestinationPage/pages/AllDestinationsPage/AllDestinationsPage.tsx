import React from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { Button, MainPageWithScroll } from "components";
import { EmptyResourceListView } from "components/EmptyResourceListView";
import HeadTitle from "components/HeadTitle";
import PageTitle from "components/PageTitle";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useDestinationList } from "hooks/services/useDestinationHook";

import { RoutePaths } from "../../../routePaths";
import DestinationsTable from "./components/DestinationsTable";

const AllDestinationsPage: React.FC = () => {
  const navigate = useNavigate();
  const { destinations } = useDestinationList();
  useTrackPage(PageTrackingCodes.DESTINATION_LIST);

  const onCreateDestination = () => navigate(`${RoutePaths.DestinationNew}`);

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
