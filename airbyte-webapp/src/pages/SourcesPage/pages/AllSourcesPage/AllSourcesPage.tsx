import React from "react";
import { FormattedMessage } from "react-intl";

import { Button, MainPageWithScroll } from "components";
import { EmptyResourceListView } from "components/EmptyResourceListView";
import HeadTitle from "components/HeadTitle";
import PageTitle from "components/PageTitle";

import { useSourceList } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";

import { RoutePaths } from "../../../routePaths";
import SourcesTable from "./components/SourcesTable";

const AllSourcesPage: React.FC = () => {
  const { push } = useRouter();
  const { sources } = useSourceList();

  const onCreateSource = () => push(`${RoutePaths.SourceNew}`);
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
