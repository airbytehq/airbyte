import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource } from "rest-hooks";

import PageTitle from "../../../../components/PageTitle";
import useRouter from "../../../../components/hooks/useRouterHook";
import config from "../../../../config";
import ContentCard from "../../../../components/ContentCard";
import EmptyResource from "../../../../components/EmptyResourceBlock";
import ConnectionResource from "../../../../core/resources/Connection";
import SourceResource from "../../../../core/resources/Source";
import { Routes } from "../../../routes";
import Breadcrumbs from "../../../../components/Breadcrumbs";
import SourceConnectionTable from "./components/SourceConnectionTable";
import SourceSettings from "./components/SourceSettings";
import {
  ItemTabs,
  StepsTypes,
  TableItemTitle
} from "../../../../components/SourceAndDestinationsBlocks";
import LoadingPage from "../../../../components/LoadingPage";

const Content = styled(ContentCard)`
  margin: 0 32px 0 27px;
`;

const SourceItemPage: React.FC = () => {
  const { query, history, push } = useRouter();

  const [currentStep, setCurrentStep] = useState<string>(StepsTypes.OVERVIEW);
  const onSelectStep = (id: string) => setCurrentStep(id);

  const source = useResource(SourceResource.detailShape(), {
    // @ts-ignore
    sourceId: query.id
  });

  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });

  const onClickBack = () =>
    history.length > 2 ? history.goBack() : push(Routes.Source);

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="sidebar.sources" />,
      onClick: onClickBack
    },
    { name: source.name }
  ];

  const connectionsWithSource = connections.filter(
    connectionItem => connectionItem.sourceId === source.sourceId
  );

  const renderContent = () => {
    if (currentStep === StepsTypes.SETTINGS) {
      return <SourceSettings currentSource={source} />;
    }

    return (
      <>
        <TableItemTitle type="destination" />
        {connectionsWithSource.length ? (
          <SourceConnectionTable connections={connectionsWithSource} />
        ) : (
          <Content>
            <EmptyResource
              text={<FormattedMessage id="sources.noDestinations" />}
              description={
                <FormattedMessage id="sources.addDestinationReplicateData" />
              }
            />
          </Content>
        )}
      </>
    );
  };

  return (
    <>
      <PageTitle
        title={<Breadcrumbs data={breadcrumbsData} />}
        middleComponent={
          <ItemTabs currentStep={currentStep} setCurrentStep={onSelectStep} />
        }
        withLine
      />
      <Suspense fallback={<LoadingPage />}>{renderContent()}</Suspense>
    </>
  );
};

export default SourceItemPage;
