import React, { Suspense, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { Route, Routes, useNavigate, useParams } from "react-router-dom";

import { LoadingPage } from "components";
import ApiErrorBoundary from "components/ApiErrorBoundary";
import { ItemTabs, StepsTypes, TableItemTitle } from "components/ConnectorBlocks";
import { ConnectorIcon } from "components/ConnectorIcon";
import HeadTitle from "components/HeadTitle";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import { Breadcrumbs } from "components/ui/Breadcrumbs";
import { DropDownOptionDataItem } from "components/ui/DropDown";
import { PageHeader } from "components/ui/PageHeader";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useSourceList } from "hooks/services/useSourceHook";
import { RoutePaths } from "pages/routePaths";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { getIcon } from "utils/imageUtils";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";

import { useGetDestination } from "../../../../hooks/services/useDestinationHook";
import DestinationConnectionTable from "./components/DestinationConnectionTable";
import DestinationSettings from "./components/DestinationSettings";

const DestinationItemPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.DESTINATION_ITEM);
  const params = useParams() as { "*": StepsTypes | ""; id: string };
  const navigate = useNavigate();
  const currentStep = useMemo<string>(() => (params["*"] === "" ? StepsTypes.OVERVIEW : params["*"]), [params]);

  const { sources } = useSourceList();

  const { sourceDefinitions } = useSourceDefinitionList();

  const destination = useGetDestination(params.id);

  const destinationDefinition = useDestinationDefinition(destination.destinationDefinitionId);

  const { connections } = useConnectionList();

  const onClickBack = () => navigate("..");

  const onSelectStep = (id: string) => {
    const path = id === StepsTypes.OVERVIEW ? "." : id.toLowerCase();
    navigate(path);
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

  const onSelect = (data: DropDownOptionDataItem) => {
    const path = `../${RoutePaths.ConnectionNew}`;
    const state =
      data.value === "create-new-item"
        ? { destinationId: destination.destinationId }
        : {
            sourceId: data.value,
            destinationId: destination.destinationId,
          };

    navigate(path, { state });
  };

  return (
    <ConnectorDocumentationWrapper>
      <HeadTitle titles={[{ id: "admin.destinations" }, { title: destination.name }]} />

      <PageHeader
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
