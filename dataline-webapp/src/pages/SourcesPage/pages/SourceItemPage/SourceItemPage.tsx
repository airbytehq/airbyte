import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import PageTitle from "../../../../components/PageTitle";
import Breadcrumbs from "../../../../components/Breadcrumbs";
import useRouter from "../../../../components/hooks/useRouterHook";
import { Routes } from "../../../routes";

const Content = styled.div`
  max-width: 816px;
  margin: 18px auto;
`;

const SourceItemPage: React.FC = () => {
  // TODO: change to real data
  const sourceData = {
    name: "Source Name",
    source: "Source",
    destination: "Destination",
    frequency: "5m",
    enabled: true
  };

  const { push, history } = useRouter();
  const onClickBack = () =>
    history.length > 2 ? history.goBack() : push(Routes.Source);

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="sidebar.sources" />,
      onClick: onClickBack
    },
    { name: sourceData.name }
  ];
  return (
    <>
      <PageTitle
        withLine
        title={<Breadcrumbs data={breadcrumbsData} />}
        middleComponent={<div />}
      />
      <Content>SOURCE PAGE</Content>
    </>
  );
};

export default SourceItemPage;
