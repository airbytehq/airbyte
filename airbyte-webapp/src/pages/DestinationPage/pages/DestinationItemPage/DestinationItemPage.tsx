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
import { Routes } from "../../../routes";
import Breadcrumbs from "../../../../components/Breadcrumbs";
import DestinationConnectionTable from "./components/DestinationConnectionTable";
import DestinationResource from "../../../../core/resources/Destination";
import {
  ItemTabs,
  StepsTypes,
  TableItemTitle
} from "../../../../components/SourceAndDestinationsBlocks";
import DestinationSettings from "./components/DestinationSettings";
import LoadingPage from "../../../../components/LoadingPage";

const Content = styled(ContentCard)`
  margin: 0 32px 0 27px;
`;

const DestinationItemPage: React.FC = () => {
  const { query, history, push } = useRouter();

  const [currentStep, setCurrentStep] = useState<string>(StepsTypes.OVERVIEW);
  const onSelectStep = (id: string) => setCurrentStep(id);

  const destination = useResource(DestinationResource.detailShape(), {
    // @ts-ignore
    destinationId: query.id
  });

  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });

  const onClickBack = () =>
    history.length > 2 ? history.goBack() : push(Routes.Destination);

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="admin.destinations" />,
      onClick: onClickBack
    },
    { name: destination.name }
  ];

  const connectionsWithDestination = connections.filter(
    connectionItem => connectionItem.destinationId === destination.destinationId
  );

  const renderContent = () => {
    if (currentStep === StepsTypes.SETTINGS) {
      return <DestinationSettings currentDestination={destination} />;
    }

    return (
      <>
        <TableItemTitle type="source" />
        {connectionsWithDestination.length ? (
          <DestinationConnectionTable
            connections={connectionsWithDestination}
          />
        ) : (
          <Content>
            <EmptyResource
              text={<FormattedMessage id="destinations.noSources" />}
              description={
                <FormattedMessage id="destinations.addSourceReplicateData" />
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
        withLine
        middleComponent={
          <ItemTabs currentStep={currentStep} setCurrentStep={onSelectStep} />
        }
      />
      <Suspense fallback={<LoadingPage />}>{renderContent()}</Suspense>
    </>
  );
};

export default DestinationItemPage;
