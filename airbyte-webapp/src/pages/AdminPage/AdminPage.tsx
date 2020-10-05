import React from "react";
import { FormattedMessage } from "react-intl";

import MainPageWithScroll from "../../components/MainPageWithScroll";
import PageTitle from "../../components/PageTitle";

const AdminPage: React.FC = () => {
  return (
    <MainPageWithScroll
      title={
        <PageTitle withLine title={<FormattedMessage id={"sidebar.admin"} />} />
      }
    />
  );
};

export default AdminPage;
