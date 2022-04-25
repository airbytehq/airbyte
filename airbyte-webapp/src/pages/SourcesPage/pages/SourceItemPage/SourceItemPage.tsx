import React, { Suspense, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { Route, Routes } from "react-router-dom";

import { DropDownRow } from "components";
import PageTitle from "components/PageTitle";
import Breadcrumbs from "components/Breadcrumbs";
import { ItemTabs, StepsTypes, TableItemTitle } from "components/ConnectorBlocks";
import LoadingPage from "components/LoadingPage";
import MainPageWithScroll from "components/MainPageWithScroll";
import HeadTitle from "components/HeadTitle";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import { ConnectorIcon } from "components/ConnectorIcon";

import { getIcon } from "utils/imageUtils";
import useRouter from "hooks/useRouter";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useGetSource } from "hooks/services/useSourceHook";

import { RoutePaths } from "../../../routePaths";
import { useDestinationList } from "../../../../hooks/services/useDestinationHook";
import SourceSettings from "./components/SourceSettings";
import SourceConnectionTable from "./components/SourceConnectionTable";

const SourceItemPage: React.FC = () => {
  const { query, params, push } = useRouter<{ id: string }, { id: string; "*": string }>();
  const currentStep = useMemo<string>(() => (params["*"] === "" ? StepsTypes.OVERVIEW : params["*"]), [params]);

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

  const connectionsWithSource = connections.filter((connectionItem) => connectionItem.sourceId === source.sourceId);

  const destinationsDropDownData = useMemo(
    () =>
      destinations.map((item) => {
        const destinationDef = destinationDefinitions.find(
          (dd) => dd.destinationDefinitionId === item.destinationDefinitionId
        );
        return {
          label: item.name,
          value: item.destinationId,
          img: <ConnectorIcon icon={destinationDef?.icon} />,
        };
      }),
    [destinations, destinationDefinitions]
  );

  const onSelectStep = (id: string) => {
    const path = id === StepsTypes.OVERVIEW ? "/" : `/${id.toLowerCase()}`;
    push(`/source/${source.sourceId}${path}`);
  };

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

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "admin.sources" }, { title: source.name }]} />}
      pageTitle={
        <PageTitle
          title={<Breadcrumbs data={breadcrumbsData} />}
          middleComponent={<ItemTabs currentStep={currentStep} setCurrentStep={onSelectStep} />}
          withLine
        />
      }
    >
      <Suspense fallback={<LoadingPage />}>
        <Routes>
          <Route
            path="/settings"
            element={<SourceSettings currentSource={source} connectionsWithSource={connectionsWithSource} />}
          />
          <Route
            index
            element={
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
            }
          ></Route>
        </Routes>
      </Suspense>
    </MainPageWithScroll>
  );
};

export default SourceItemPage;
