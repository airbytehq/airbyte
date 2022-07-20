import React from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { Button, MainPageWithScroll } from "components";
import { EmptyResourceListView } from "components/EmptyResourceListView";
import HeadTitle from "components/HeadTitle";
import PageTitle from "components/PageTitle";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useSourceList } from "hooks/services/useSourceHook";

import { RoutePaths } from "../../../routePaths";
import SourcesTable from "./components/SourcesTable";

const AllSourcesPage: React.FC = () => {
  const navigate = useNavigate();
  const { sources } = useSourceList();
  useTrackPage(PageTrackingCodes.SOURCE_LIST);
  const onCreateSource = () => navigate(`${RoutePaths.SourceNew}`);
  return sources.length ? (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "admin.sources" }]} />}
      pageTitle={
        <PageTitle
          title={<FormattedMessage id="sidebar.sources" />}
          endComponent={
            <Button onClick={onCreateSource} data-id="new-source">
              <FormattedMessage id="sources.newSource" />
            </Button>
          }
        />
      }
    >
      <SourcesTable sources={sources} />
    </MainPageWithScroll>
  ) : (
    <EmptyResourceListView resourceType="sources" onCreateClick={onCreateSource} />
  );
};

export default AllSourcesPage;
