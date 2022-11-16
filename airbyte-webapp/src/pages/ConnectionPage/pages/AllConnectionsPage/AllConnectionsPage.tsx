import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { Suspense } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useNavigate } from "react-router-dom";

import { LoadingPage, MainPageWithScroll } from "components";
import { EmptyResourceListView } from "components/common/EmptyResourceListView";
import { HeadTitle } from "components/common/HeadTitle";
import { Button } from "components/ui/Button";
import { PageHeader } from "components/ui/PageHeader";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { links } from "utils/links";

import { RoutePaths } from "../../../routePaths";
import styles from "./AllConnectionsPage.module.scss";
import ConnectionsTable from "./components/ConnectionsTable";

const AllConnectionsPage: React.FC = () => {
  const navigate = useNavigate();
  const { formatMessage } = useIntl();

  useTrackPage(PageTrackingCodes.CONNECTIONS_LIST);
  const { connections } = useConnectionList();

  const onCreateClick = () => navigate(`${RoutePaths.ConnectionNew}`);

  return (
    <Suspense fallback={<LoadingPage />}>
      {connections.length ? (
        <MainPageWithScroll
          headTitle={<HeadTitle titles={[{ id: "sidebar.connections" }]} />}
          pageTitle={
            <PageHeader
              title={<FormattedMessage id="sidebar.connections" />}
              endComponent={
                <Button icon={<FontAwesomeIcon icon={faPlus} />} variant="primary" size="sm" onClick={onCreateClick}>
                  <FormattedMessage id="connection.newConnection" />
                </Button>
              }
            />
          }
        >
          <ConnectionsTable connections={connections} />
        </MainPageWithScroll>
      ) : (
        <EmptyResourceListView
          resourceType="connections"
          onCreateClick={onCreateClick}
          buttonLabel={formatMessage({ id: "connection.createFirst" })}
          footer={
            <FormattedMessage
              id="connection.emptyStateFooter"
              values={{
                demoLnk: (children: React.ReactNode) => (
                  <a href={links.demoLink} target="_blank" rel="noreferrer noopener" className={styles.link}>
                    {children}
                  </a>
                ),
              }}
            />
          }
        />
      )}
    </Suspense>
  );
};

export default AllConnectionsPage;
