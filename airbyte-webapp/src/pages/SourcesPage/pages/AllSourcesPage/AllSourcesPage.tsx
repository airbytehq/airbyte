import React from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import { Button, MainPageWithScroll } from "components";
import { Routes } from "../../../routes";
import PageTitle from "components/PageTitle";
import useRouter from "components/hooks/useRouterHook";
import SourcesTable from "./components/SourcesTable";
import config from "config";
import SourceResource from "core/resources/Source";
import HeadTitle from "components/HeadTitle";
import Placeholder, { ResourceTypes } from "components/Placeholder";

const AllSourcesPage: React.FC = () => {
  const { push } = useRouter();

  const { sources } = useResource(SourceResource.listShape(), {
    workspaceId: config.ui.workspaceId,
  });

  const onCreateSource = () => push(`${Routes.Source}${Routes.SourceNew}`);
  return (
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
      {sources.length ? (
        <SourcesTable sources={sources} />
      ) : (
        <Placeholder resource={ResourceTypes.Sources} />
      )}
    </MainPageWithScroll>
  );
};

export default AllSourcesPage;
