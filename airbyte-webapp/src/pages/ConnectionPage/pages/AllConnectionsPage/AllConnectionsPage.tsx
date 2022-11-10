import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";

import { Button, LoadingPage, MainPageWithScroll, PageTitle } from "components";
// import { EmptyResourceListView } from "components/EmptyResourceListView";
import HeadTitle from "components/HeadTitle";

// import WelcomeStep from "../../../OnboardingPage/components/WelcomeStep";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useConnectionList } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";

import OnboardingPage from "../../../OnboardingPage";
import { RoutePaths } from "../../../routePaths";
import ConnectionsTable from "./components/ConnectionsTable";

const AllConnectionsPage: React.FC = () => {
  const { push } = useRouter();

  useTrackPage(PageTrackingCodes.CONNECTIONS_LIST);
  const { connections } = useConnectionList();

  // const connections = [
  //   {
  //     name: "Amazon Ads <> MySQL",
  //     status: "Active",
  //     lastSync: 1,
  //     entityName: "Amazon Ads",
  //     connectorName: "MySQL",
  //     connectionId: "",
  //     lastSyncStatus: "1 day ago",
  //     enabled: true,
  //   },
  //   {
  //     name: "Amazon Seller Partner ...",
  //     status: "Inactive",
  //     lastSync: 2,
  //     entityName: "Amazon Seller Partner",
  //     connectorName: "Snowflake",
  //     connectionId: "",
  //     lastSyncStatus: "1 hour ago",
  //     enabled: false,
  //   },
  //   {
  //     name: "Amazon Ads <> MySQL",
  //     status: "Active",
  //     lastSync: 3,
  //     entityName: "Amazon Ads",
  //     connectorName: "MySQL",
  //     connectionId: "",
  //     lastSyncStatus: "1 day ago",
  //     enabled: true,
  //   },
  //   {
  //     name: "Amazon Seller Partner ...",
  //     status: "Inactive",
  //     lastSync: 4,
  //     entityName: "Amazon Seller Partner",
  //     connectorName: "Snowflake",
  //     connectionId: "",
  //     lastSyncStatus: "1 hour ago",
  //     enabled: false,
  //   },
  //   {
  //     name: "Amazon Ads <> MySQL",
  //     status: "Active",
  //     lastSync: 5,
  //     entityName: "Amazon Ads",
  //     connectorName: "MySQL",
  //     connectionId: "",
  //     lastSyncStatus: "1 day ago",
  //     enabled: true,
  //   },
  // ];

  const allowCreateConnection = useFeature(FeatureItem.AllowCreateConnection);

  const onCreateClick = () => push(`${RoutePaths.ConnectionNew}`);

  // console.log( connections );

  return (
    <Suspense fallback={<LoadingPage />}>
      {connections.length ? (
        <MainPageWithScroll
          headTitle={<HeadTitle titles={[{ title: "Connections" }]} />}
          pageTitle={
            <PageTitle
              title=""
              endComponent={
                <Button onClick={onCreateClick} disabled={!allowCreateConnection} size="lg">
                  <FormattedMessage id="connection.newConnection" />
                </Button>
              }
            />
          }
        >
          <ConnectionsTable connections={connections} />
        </MainPageWithScroll>
      ) : (
        // <EmptyResourceListView
        //   resourceType="connections"
        //   onCreateClick={onCreateClick}
        //   disableCreateButton={!allowCreateConnection}
        // />
        <OnboardingPage />
      )}
    </Suspense>
  );
};

export default AllConnectionsPage;
