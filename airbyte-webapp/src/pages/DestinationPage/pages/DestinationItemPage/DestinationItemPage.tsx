import React, { Suspense, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { Route, Routes } from "react-router-dom";

import Placeholder, { ResourceTypes } from "components/Placeholder";
import Breadcrumbs from "components/Breadcrumbs";
import { ItemTabs, StepsTypes, TableItemTitle } from "components/ConnectorBlocks";
import HeadTitle from "components/HeadTitle";
import { DropDownRow, LoadingPage, MainPageWithScroll, PageTitle } from "components";
import { ConnectorIcon } from "components/ConnectorIcon";

import { getIcon } from "utils/imageUtils";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceList } from "hooks/services/useSourceHook";

import { useGetDestination } from "../../../../hooks/services/useDestinationHook";
import DestinationSettings from "./components/DestinationSettings";
import DestinationConnectionTable from "./components/DestinationConnectionTable";

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
    const path = id === StepsTypes.OVERVIEW ? "/" : `/${id.toLowerCase()}`;
    push(`/destination/${destination.destinationId}${path}`);
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
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "admin.destinations" }, { title: destination.name }]} />}
      pageTitle={
        <PageTitle
          title={<Breadcrumbs data={breadcrumbsData} />}
          withLine
          middleComponent={<ItemTabs currentStep={currentStep} setCurrentStep={onSelectStep} />}
        />
      }
    >
      <Suspense fallback={<LoadingPage />}>
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
      </Suspense>
    </MainPageWithScroll>
  );
};

export default DestinationItemPage;
