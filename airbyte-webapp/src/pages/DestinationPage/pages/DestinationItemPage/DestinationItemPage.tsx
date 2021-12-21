import React, { Suspense, useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import PageTitle from "components/PageTitle";
import useRouter from "hooks/useRouter";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import ConnectionResource from "core/resources/Connection";
import { RoutePaths } from "pages/routes";
import Breadcrumbs from "components/Breadcrumbs";
import DestinationConnectionTable from "./components/DestinationConnectionTable";
import DestinationResource from "core/resources/Destination";
import {
  ItemTabs,
  StepsTypes,
  TableItemTitle,
} from "components/ConnectorBlocks";
import DestinationSettings from "./components/DestinationSettings";
import LoadingPage from "components/LoadingPage";
import SourceResource from "core/resources/Source";
import MainPageWithScroll from "components/MainPageWithScroll";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import { getIcon } from "utils/imageUtils";
import ImageBlock from "components/ImageBlock";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import HeadTitle from "components/HeadTitle";
import useWorkspace from "hooks/services/useWorkspace";
import { DropDownRow } from "components";

const DestinationItemPage: React.FC = () => {
  const { params, push } = useRouter<unknown, { id: string }>();
  const { workspace } = useWorkspace();
  const [currentStep, setCurrentStep] = useState<string>(StepsTypes.OVERVIEW);
  const onSelectStep = (id: string) => setCurrentStep(id);

  const { sources } = useResource(SourceResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });

  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {
      workspaceId: workspace.workspaceId,
    }
  );

  const destination = useResource(DestinationResource.detailShape(), {
    destinationId: params.id,
  });

  const destinationDefinition = useResource(
    DestinationDefinitionResource.detailShape(),
    {
      destinationDefinitionId: destination.destinationDefinitionId,
    }
  );

  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });

  const onClickBack = () => push("..");

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
      sources.map((item) => {
        const sourceDef = sourceDefinitions.find(
          (sd) => sd.sourceDefinitionId === item.sourceDefinitionId
        );
        return {
          label: item.name,
          value: item.sourceId,
          img: <ImageBlock img={sourceDef?.icon} />,
        };
      }),
    [sources, sourceDefinitions]
  );

  const onSelect = (data: DropDownRow.IDataItem) => {
    const path = `../${RoutePaths.ConnectionNew}`;
    const state =
      data.value === "create-new-item"
        ? { destinationId: destination.destinationId }
        : {
            sourceId: data.value,
            destinationId: destination.destinationId,
          };

    push(path, { state });
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
          entityIcon={
            destinationDefinition.icon
              ? getIcon(destinationDefinition.icon)
              : null
          }
        />
        {connectionsWithDestination.length ? (
          <DestinationConnectionTable
            connections={connectionsWithDestination}
          />
        ) : (
          <Placeholder resource={ResourceTypes.Sources} />
        )}
      </>
    );
  };

  return (
    <MainPageWithScroll
      headTitle={
        <HeadTitle
          titles={[{ id: "admin.destinations" }, { title: destination.name }]}
        />
      }
      pageTitle={
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
