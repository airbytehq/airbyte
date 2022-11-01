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
import { useSourceList } from "hooks/services/useSourceHook";

import { RoutePaths } from "../../../routePaths";
import SourcesTable from "./components/SourcesTable";

const AllSourcesPage: React.FC = () => {
  const navigate = useNavigate();
  const { formatMessage } = useIntl();
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
    <EmptyResourceListView
      resourceType="sources"
      onCreateClick={onCreateSource}
      buttonLabel={formatMessage({ id: "sources.createFirst" })}
    />
  );
};

export default AllSourcesPage;
