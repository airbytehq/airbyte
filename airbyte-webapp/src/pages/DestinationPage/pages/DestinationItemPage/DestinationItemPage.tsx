import React, { Suspense, useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource } from "rest-hooks";

import PageTitle from "components/PageTitle";
import useRouter from "components/hooks/useRouterHook";
import config from "config";
import ContentCard from "components/ContentCard";
import EmptyResource from "components/EmptyResourceBlock";
import ConnectionResource from "core/resources/Connection";
import { Routes } from "../../../routes";
import Breadcrumbs from "components/Breadcrumbs";
import DestinationConnectionTable from "./components/DestinationConnectionTable";
import DestinationResource from "core/resources/Destination";
import {
  ItemTabs,
  StepsTypes,
  TableItemTitle,
} from "components/SourceAndDestinationsBlocks";
import DestinationSettings from "./components/DestinationSettings";
import LoadingPage from "components/LoadingPage";
import SourceResource from "core/resources/Source";
import MainPageWithScroll from "components/MainPageWithScroll";

const Content = styled(ContentCard)`
  margin: 0 32px 0 27px;
`;

const DestinationItemPage: React.FC = () => {
  const { query, push } = useRouter<{ id: string }>();

  const [currentStep, setCurrentStep] = useState<string>(StepsTypes.OVERVIEW);
  const onSelectStep = (id: string) => setCurrentStep(id);

  const { sources } = useResource(SourceResource.listShape(), {
    workspaceId: config.ui.workspaceId,
  });

  const destination = useResource(DestinationResource.detailShape(), {
    destinationId: query.id,
  });

  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: config.ui.workspaceId,
  });

  const onClickBack = () => push(Routes.Destination);

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="admin.destinations" />,
      onClick: onClickBack,
    },
    { name: destination.name },
  ];

  const connectionsWithDestination = connections.filter(
    (connectionItem) =>
      connectionItem.destinationId === destination.destinationId
  );

  const sourcesDropDownData = useMemo(
    () =>
      sources.map((item) => ({
        text: item.name,
        value: item.sourceId,
        img: "/default-logo-catalog.svg",
      })),
    [sources]
  );

  const onSelect = (data: { value: string }) => {
    if (data.value === "create-new-item") {
      push({
        pathname: `${Routes.Destination}${Routes.ConnectionNew}`,
        state: { destinationId: destination.destinationId },
      });
    } else {
      push({
        pathname: `${Routes.Destination}${Routes.ConnectionNew}`,
        state: {
          sourceId: data.value,
          destinationId: destination.destinationId,
        },
      });
    }
  };

  const renderContent = () => {
    if (currentStep === StepsTypes.SETTINGS) {
      return (
        <DestinationSettings
          currentDestination={destination}
          connectionsWithDestination={connectionsWithDestination}
        />
      );
    }

    return (
      <>
        <TableItemTitle
          type="source"
          dropDownData={sourcesDropDownData}
          onSelect={onSelect}
          entityName={destination.name}
          entity={destination.destinationName}
        />
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
    <MainPageWithScroll
      title={
        <PageTitle
          title={<Breadcrumbs data={breadcrumbsData} />}
          withLine
          middleComponent={
            <ItemTabs currentStep={currentStep} setCurrentStep={onSelectStep} />
          }
        />
      }
    >
      <Suspense fallback={<LoadingPage />}>{renderContent()}</Suspense>
    </MainPageWithScroll>
  );
};

export default DestinationItemPage;
