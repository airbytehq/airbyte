import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { LoadingPage, MainPageWithScroll } from "components";
import { HeadTitle } from "components/common/HeadTitle";
import { ConnectionOnboarding } from "components/connection/ConnectionOnboarding";
import { Button } from "components/ui/Button";
import { PageHeader } from "components/ui/PageHeader";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useConnectionList } from "hooks/services/useConnectionHook";

import ConnectionsTable from "./ConnectionsTable";
import { RoutePaths } from "../../routePaths";

export const AllConnectionsPage: React.FC = () => {
  const navigate = useNavigate();

  useTrackPage(PageTrackingCodes.CONNECTIONS_LIST);
  const { connections } = useConnectionList();

  const onCreateClick = (sourceDefinitionId?: string) =>
    navigate(`${RoutePaths.ConnectionNew}`, { state: { sourceDefinitionId } });

  return (
    <Suspense fallback={<LoadingPage />}>
      {connections.length ? (
        <MainPageWithScroll
          headTitle={<HeadTitle titles={[{ id: "sidebar.connections" }]} />}
          pageTitle={
            <PageHeader
              title={<FormattedMessage id="sidebar.connections" />}
              endComponent={
                <Button
                  icon={<FontAwesomeIcon icon={faPlus} />}
                  variant="primary"
                  size="sm"
                  onClick={() => onCreateClick()}
                >
                  <FormattedMessage id="connection.newConnection" />
                </Button>
              }
            />
          }
        >
          <ConnectionsTable connections={connections} />
        </MainPageWithScroll>
      ) : (
        <ConnectionOnboarding onCreate={onCreateClick} />
      )}
    </Suspense>
  );
};
