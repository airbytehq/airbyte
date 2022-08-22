import React, { Suspense, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { Route, Routes } from "react-router-dom";

import { DropDownRow, LoadingPage, PageTitle } from "components";
import ApiErrorBoundary from "components/ApiErrorBoundary";
import Breadcrumbs from "components/Breadcrumbs";
import { ItemTabs, StepsTypes, TableItemTitle } from "components/ConnectorBlocks";
import { ConnectorIcon } from "components/ConnectorIcon";
import HeadTitle from "components/HeadTitle";
import Placeholder, { ResourceTypes } from "components/Placeholder";

import { useConnectionList } from "hooks/services/useConnectionHook";
import { useSourceList } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { getIcon } from "utils/imageUtils";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";

import { useGetDestination } from "../../../../hooks/services/useDestinationHook";
import DestinationConnectionTable from "./components/DestinationConnectionTable";
import DestinationSettings from "./components/DestinationSettings";

const DestinationItemPage: React.FC = () => {
  const { params, push } = useRouter<unknown, { id: string; "*": string }>();
  const currentStep = useMemo<string>(() => (params["*"] === "" ? StepsTypes.OVERVIEW : params["*"]), [params]);

  const { sources } = useSourceList();

  const { sourceDefinitions } = useSourceDefinitionList();

  const destination = useGetDestination(params.id);

  const destinationDefinition = useDestinationDefinition(destination.destinationDefinitionId);

  const { connections } = useConnectionList();

  const onClickBack = () => push("..");

  const onSelectStep = (id: string) => {
    const path = id === StepsTypes.OVERVIEW ? "." : id.toLowerCase();
    push(path);
  };

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="admin.destinations" />,
      onClick: onClickBack,
    },
    { name: destination.name },
  ];

  const connectionsWithDestination = connections.filter(
    (connectionItem) => connectionItem.destinationId === destination.destinationId
  );

  const sourcesDropDownData = useMemo(
    () =>
      sources.map((item) => {
        const sourceDef = sourceDefinitions.find((sd) => sd.sourceDefinitionId === item.sourceDefinitionId);
        return {
          label: item.name,
          value: item.sourceId,
          img: <ConnectorIcon icon={sourceDef?.icon} />,
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

  return (
    <ConnectorDocumentationWrapper>
      <HeadTitle titles={[{ id: "admin.destinations" }, { title: destination.name }]} />

      <PageTitle
        title={<Breadcrumbs data={breadcrumbsData} />}
        middleComponent={<ItemTabs currentStep={currentStep} setCurrentStep={onSelectStep} />}
      />

      <Suspense fallback={<LoadingPage />}>
        <ApiErrorBoundary>
          <Routes>
            <Route
              path="/settings"
              element={
                <DestinationSettings
                  currentDestination={destination}
                  connectionsWithDestination={connectionsWithDestination}
                />
              }
            />
            <Route
              index
              element={
                <>
                  <TableItemTitle
                    type="source"
                    dropDownData={sourcesDropDownData}
                    onSelect={onSelect}
                    entityName={destination.name}
                    entity={destination.destinationName}
                    entityIcon={destinationDefinition.icon ? getIcon(destinationDefinition.icon) : null}
                    releaseStage={destinationDefinition.releaseStage}
                  />
                  {connectionsWithDestination.length ? (
                    <DestinationConnectionTable connections={connectionsWithDestination} />
                  ) : (
                    <Placeholder resource={ResourceTypes.Sources} />
                  )}
                </>
              }
            />
          </Routes>
        </ApiErrorBoundary>
      </Suspense>
    </ConnectorDocumentationWrapper>
  );
};

export default DestinationItemPage;
