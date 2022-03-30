import React from "react";
import { FormattedMessage } from "react-intl";

import { Button, MainPageWithScroll } from "components";
import PageTitle from "components/PageTitle";
import useRouter from "hooks/useRouter";
import SourcesTable from "./components/SourcesTable";
import HeadTitle from "components/HeadTitle";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import { RoutePaths } from "../../../routePaths";
import { useSourceList } from "hooks/services/useSourceHook";

const AllSourcesPage: React.FC = () => {
  const { push } = useRouter();
  const { sources } = useSourceList();

  const onCreateSource = () => push(`${RoutePaths.SourceNew}`);
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
