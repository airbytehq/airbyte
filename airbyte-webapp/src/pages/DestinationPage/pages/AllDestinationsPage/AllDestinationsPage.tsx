import React from "react";
import { FormattedMessage } from "react-intl";

import { Button, MainPageWithScroll } from "components";
import PageTitle from "components/PageTitle";
import useRouter from "hooks/useRouter";
import DestinationsTable from "./components/DestinationsTable";
import HeadTitle from "components/HeadTitle";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import { RoutePaths } from "../../../routePaths";
import { useDestinationList } from "hooks/services/useDestinationHook";

const AllDestinationsPage: React.FC = () => {
  const { push } = useRouter();
  const { destinations } = useDestinationList();

  const onCreateDestination = () => push(`${RoutePaths.DestinationNew}`);

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "admin.destinations" }]} />}
      pageTitle={
        <PageTitle
          title={<FormattedMessage id="admin.destinations" />}
          endComponent={
            <Button onClick={onCreateDestination} data-id="new-destination">
              <FormattedMessage id="destination.newDestination" />
            </Button>
          }
        />
      }
    >
      {destinations.length ? (
        <DestinationsTable destinations={destinations} />
      ) : (
        <Placeholder resource={ResourceTypes.Destinations} />
      )}
    </MainPageWithScroll>
  );
};

export default AllDestinationsPage;
