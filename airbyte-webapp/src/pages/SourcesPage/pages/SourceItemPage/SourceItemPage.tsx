import React, { Suspense, useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import { DropDownRow, ImageBlock } from "components";
import PageTitle from "components/PageTitle";
import useRouter from "hooks/useRouter";
import Breadcrumbs from "components/Breadcrumbs";
import {
  ItemTabs,
  StepsTypes,
  TableItemTitle,
} from "components/ConnectorBlocks";
import LoadingPage from "components/LoadingPage";
import MainPageWithScroll from "components/MainPageWithScroll";

import SourceConnectionTable from "./components/SourceConnectionTable";
import SourceSettings from "./components/SourceSettings";
import SourceResource from "core/resources/Source";

import DestinationResource from "core/resources/Destination";
import { getIcon } from "utils/imageUtils";
import HeadTitle from "components/HeadTitle";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { RoutePaths } from "../../../routePaths";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";

const SourceItemPage: React.FC = () => {
  const { query, push } = useRouter<{ id: string }>();
  const workspace = useCurrentWorkspace();
  const [currentStep, setCurrentStep] = useState<string>(StepsTypes.OVERVIEW);
  const onSelectStep = (id: string) => setCurrentStep(id);

  const { destinations } = useResource(DestinationResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });

  const { destinationDefinitions } = useDestinationDefinitionList();

  const source = useResource(SourceResource.detailShape(), {
    sourceId: query.id,
  });

  const sourceDefinition = useSourceDefinition(source?.sourceDefinitionId);

  const { connections } = useConnectionList();

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="sidebar.sources" />,
      onClick: () => push(".."),
    },
    { name: source.name },
  ];

  const connectionsWithSource = connections.filter(
    (connectionItem) => connectionItem.sourceId === source.sourceId
  );

  const destinationsDropDownData = useMemo(
    () =>
      destinations.map((item) => {
        const destinationDef = destinationDefinitions.find(
          (dd) => dd.destinationDefinitionId === item.destinationDefinitionId
        );
        return {
          label: item.name,
          value: item.destinationId,
          img: <ImageBlock img={destinationDef?.icon} />,
        };
      }),
    [destinations, destinationDefinitions]
  );

  const onSelect = (data: DropDownRow.IDataItem) => {
    const path = `../${RoutePaths.ConnectionNew}`;
    const state =
      data.value === "create-new-item"
        ? { sourceId: source.sourceId }
        : {
            destinationId: data.value,
            sourceId: source.sourceId,
          };

    push(path, { state });
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
          entityIcon={sourceDefinition ? getIcon(sourceDefinition.icon) : null}
          releaseStage={sourceDefinition.releaseStage}
        />
        {connectionsWithSource.length ? (
          <SourceConnectionTable connections={connectionsWithSource} />
        ) : (
          <Placeholder resource={ResourceTypes.Destinations} />
        )}
      </>
    );
  };

  return (
    <MainPageWithScroll
      headTitle={
        <HeadTitle titles={[{ id: "admin.sources" }, { title: source.name }]} />
      }
      pageTitle={
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
