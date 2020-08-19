import React from "react";
import { FormattedMessage } from "react-intl";

import Link from "../../../../components/Link";
import Button from "../../../../components/Button";
import { Routes } from "../../../routes";
import PageTitle from "../../../../components/PageTitle";
import useRouter from "../../../../components/hooks/useRouterHook";

const AllSourcesPage: React.FC = () => {
  const { push } = useRouter();

  const onCreateSource = () => push(`${Routes.Source}${Routes.SourceNew}`);
  return (
    <>
      <PageTitle
        title={<FormattedMessage id="sidebar.sources" />}
        endComponent={
          <Button onClick={onCreateSource}>
            <FormattedMessage id="sources.newSource" />
          </Button>
        }
      />
      <br />
      <Link to={Routes.Preferences}>Go to Preferences Form</Link>
    </>
  );
};

export default AllSourcesPage;
