import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import { Navigate, useNavigate } from "react-router-dom";

import { HeadTitle } from "components/common/HeadTitle";
import { MainPageWithScroll } from "components/common/MainPageWithScroll";
import { Button } from "components/ui/Button";
import { PageHeader } from "components/ui/PageHeader";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useSourceList } from "hooks/services/useSourceHook";

import SourcesTable from "./components/SourcesTable";
import { RoutePaths } from "../../../routePaths";

const AllSourcesPage: React.FC = () => {
  const navigate = useNavigate();
  const { sources } = useSourceList();
  useTrackPage(PageTrackingCodes.SOURCE_LIST);
  const onCreateSource = () => navigate(`${RoutePaths.SourceNew}`);
  return sources.length ? (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "admin.sources" }]} />}
      pageTitle={
        <PageHeader
          title={<FormattedMessage id="sidebar.sources" />}
          endComponent={
            <Button icon={<FontAwesomeIcon icon={faPlus} />} onClick={onCreateSource} size="sm" data-id="new-source">
              <FormattedMessage id="sources.newSource" />
            </Button>
          }
        />
      }
    >
      <SourcesTable sources={sources} />
    </MainPageWithScroll>
  ) : (
    <Navigate to={RoutePaths.SourceNew} />
  );
};

export default AllSourcesPage;
