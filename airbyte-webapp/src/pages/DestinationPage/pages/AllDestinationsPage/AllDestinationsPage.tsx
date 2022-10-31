import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useNavigate } from "react-router-dom";

import { EmptyResourceListView } from "components/common/EmptyResourceListView";
import { HeadTitle } from "components/common/HeadTitle";
import { MainPageWithScroll } from "components/common/MainPageWithScroll";
import { Button } from "components/ui/Button";
import { PageHeader } from "components/ui/PageHeader";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useDestinationList } from "hooks/services/useDestinationHook";

import { RoutePaths } from "../../../routePaths";
import DestinationsTable from "./components/DestinationsTable";

const AllDestinationsPage: React.FC = () => {
  const navigate = useNavigate();
  const { formatMessage } = useIntl();
  const { destinations } = useDestinationList();
  useTrackPage(PageTrackingCodes.DESTINATION_LIST);

  const onCreateDestination = () => navigate(`${RoutePaths.DestinationNew}`);

  return destinations.length ? (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "admin.destinations" }]} />}
      pageTitle={
        <PageHeader
          title={<FormattedMessage id="admin.destinations" />}
          endComponent={
            <Button
              icon={<FontAwesomeIcon icon={faPlus} />}
              onClick={onCreateDestination}
              size="sm"
              data-id="new-destination"
            >
              <FormattedMessage id="destinations.newDestination" />
            </Button>
          }
        />
      }
    >
      <DestinationsTable destinations={destinations} />
    </MainPageWithScroll>
  ) : (
    <EmptyResourceListView
      resourceType="destinations"
      onCreateClick={onCreateDestination}
      buttonLabel={formatMessage({ id: "destinations.createFirst" })}
    />
  );
};

export default AllDestinationsPage;
