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
import SourceResource from "core/resources/Source";
import { Routes } from "../../../routes";
import Breadcrumbs from "components/Breadcrumbs";
import SourceConnectionTable from "./components/SourceConnectionTable";
import SourceSettings from "./components/SourceSettings";
import {
  ItemTabs,
  StepsTypes,
  TableItemTitle,
} from "components/SourceAndDestinationsBlocks";
import LoadingPage from "components/LoadingPage";
import DestinationResource from "core/resources/Destination";
import MainPageWithScroll from "components/MainPageWithScroll";

const Content = styled(ContentCard)`
  margin: 0 32px 0 27px;
`;

const SourceItemPage: React.FC = () => {
  const { query, push } = useRouter<{ id: string }>();

  const [currentStep, setCurrentStep] = useState<string>(StepsTypes.OVERVIEW);
  const onSelectStep = (id: string) => setCurrentStep(id);

  const { destinations } = useResource(DestinationResource.listShape(), {
    workspaceId: config.ui.workspaceId,
  });

  const source = useResource(SourceResource.detailShape(), {
    sourceId: query.id,
  });

  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: config.ui.workspaceId,
  });

  const onClickBack = () => push(Routes.Source);

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="sidebar.sources" />,
      onClick: onClickBack,
    },
    { name: source.name },
  ];

  const connectionsWithSource = connections.filter(
    (connectionItem) => connectionItem.sourceId === source.sourceId
  );

  const destinationsDropDownData = useMemo(
    () =>
      destinations.map((item) => ({
        text: item.name,
        value: item.destinationId,
        img: "/default-logo-catalog.svg",
      })),
    [destinations]
  );

  const onSelect = (data: { value: string }) => {
    if (data.value === "create-new-item") {
      push({
        pathname: `${Routes.Source}${Routes.ConnectionNew}`,
        state: { sourceId: source.sourceId },
      });
    } else {
      push({
        pathname: `${Routes.Source}${Routes.ConnectionNew}`,
        state: { destinationId: data.value, sourceId: source.sourceId },
      });
    }
  };

  const renderContent = () => {
    if (currentStep === StepsTypes.SETTINGS) {
      return (
        <SourceSettings
          currentSource={source}
          connectionsWithSource={connectionsWithSource}
        />
      );
    }

    return (
      <>
        <TableItemTitle
          type="destination"
          dropDownData={destinationsDropDownData}
          onSelect={onSelect}
          entity={source.sourceName}
          entityName={source.name}
        />
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
    <MainPageWithScroll
      title={
        <PageTitle
          title={<Breadcrumbs data={breadcrumbsData} />}
          middleComponent={
            <ItemTabs currentStep={currentStep} setCurrentStep={onSelectStep} />
          }
          withLine
        />
      }
    >
      <Suspense fallback={<LoadingPage />}>{renderContent()}</Suspense>
    </MainPageWithScroll>
  );
};

export default SourceItemPage;
