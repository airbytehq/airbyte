import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";

import { Button, LoadingPage, MainPageWithScroll, PageTitle } from "components";
import ConnectionsTable from "./components/ConnectionsTable";
import useRouter from "hooks/useRouter";
import HeadTitle from "components/HeadTitle";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import { FeatureItem, useFeatureService } from "hooks/services/Feature";
import { RoutePaths } from "../../../routePaths";
import { useConnectionList } from "hooks/services/useConnectionHook";

const AllConnectionsPage: React.FC = () => {
  const { push } = useRouter();

  const { connections } = useConnectionList();
  const { hasFeature } = useFeatureService();
  const allowCreateConnection = hasFeature(FeatureItem.AllowCreateConnection);

  const onClick = () => push(`${RoutePaths.ConnectionNew}`);

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "sidebar.connections" }]} />}
      pageTitle={
        <PageTitle
          title={<FormattedMessage id="sidebar.connections" />}
          endComponent={
            <Button onClick={onClick} disabled={!allowCreateConnection}>
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
          <Placeholder resource={ResourceTypes.Connections} />
        )}
      </Suspense>
    </MainPageWithScroll>
  );
};

export default AllConnectionsPage;
