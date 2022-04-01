import React, { Suspense, useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";

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
import { getIcon } from "utils/imageUtils";
import HeadTitle from "components/HeadTitle";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import { RoutePaths } from "../../../routePaths";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useGetSource } from "hooks/services/useSourceHook";
import { useDestinationList } from "../../../../hooks/services/useDestinationHook";

const SourceItemPage: React.FC = () => {
  const { query, push } = useRouter<{ id: string }>();
  const [currentStep, setCurrentStep] = useState<string>(StepsTypes.OVERVIEW);
  const onSelectStep = (id: string) => setCurrentStep(id);

  const { destinations } = useDestinationList();

  const { destinationDefinitions } = useDestinationDefinitionList();

  const source = useGetSource(query.id);
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
