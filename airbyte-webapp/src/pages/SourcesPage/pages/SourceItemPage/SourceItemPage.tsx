import React, { Suspense, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { Route, Routes, useNavigate, useParams } from "react-router-dom";

import ApiErrorBoundary from "components/ApiErrorBoundary";
import { ItemTabs, StepsTypes, TableItemTitle } from "components/ConnectorBlocks";
import { ConnectorIcon } from "components/ConnectorIcon";
import HeadTitle from "components/HeadTitle";
import LoadingPage from "components/LoadingPage";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import { Breadcrumbs } from "components/ui/Breadcrumbs";
import { DropDownOptionDataItem } from "components/ui/DropDown";
import { PageHeader } from "components/ui/PageHeader";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useGetSource } from "hooks/services/useSourceHook";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { getIcon } from "utils/imageUtils";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";

import { useDestinationList } from "../../../../hooks/services/useDestinationHook";
import { RoutePaths } from "../../../routePaths";
import SourceConnectionTable from "./components/SourceConnectionTable";
import SourceSettings from "./components/SourceSettings";

const SourceItemPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.SOURCE_ITEM);
  const params = useParams<{ "*": StepsTypes | "" | undefined; id: string }>();
  const navigate = useNavigate();
  const currentStep = useMemo<StepsTypes | "" | undefined>(
    () => (params["*"] === "" ? StepsTypes.OVERVIEW : params["*"]),
    [params]
  );

  const { destinations } = useDestinationList();

  const { destinationDefinitions } = useDestinationDefinitionList();

  const source = useGetSource(params.id || "");
  const sourceDefinition = useSourceDefinition(source?.sourceDefinitionId);

  const { connections } = useConnectionList();

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="sidebar.sources" />,
      onClick: () => navigate(".."),
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
    const path = id === StepsTypes.OVERVIEW ? "." : id.toLowerCase();
    navigate(path);
  };

  const onSelect = (data: DropDownOptionDataItem) => {
    const path = `../${RoutePaths.ConnectionNew}`;
    const state =
      data.value === "create-new-item"
        ? { sourceId: source.sourceId }
        : {
            destinationId: data.value,
            sourceId: source.sourceId,
          };

    navigate(path, { state });
  };

  return (
    <ConnectorDocumentationWrapper>
      <HeadTitle titles={[{ id: "admin.sources" }, { title: source.name }]} />
      <PageHeader
        title={<Breadcrumbs data={breadcrumbsData} />}
        middleComponent={<ItemTabs currentStep={currentStep} setCurrentStep={onSelectStep} />}
      />

      <Suspense fallback={<LoadingPage />}>
        <ApiErrorBoundary>
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
            />
          </Routes>
        </ApiErrorBoundary>
      </Suspense>
    </ConnectorDocumentationWrapper>
  );
};

export default SourceItemPage;
