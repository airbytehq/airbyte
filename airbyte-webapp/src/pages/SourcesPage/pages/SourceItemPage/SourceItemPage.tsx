import React, { Suspense, useMemo } from "react";
import { useIntl } from "react-intl";
import { Route, Routes, useNavigate, useParams } from "react-router-dom";

import { ApiErrorBoundary } from "components/common/ApiErrorBoundary";
import { ConnectorIcon } from "components/common/ConnectorIcon";
import { HeadTitle } from "components/common/HeadTitle";
import { ItemTabs, StepsTypes, TableItemTitle } from "components/ConnectorBlocks";
import LoadingPage from "components/LoadingPage";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import { Breadcrumbs } from "components/ui/Breadcrumbs";
import { PageHeader } from "components/ui/PageHeader";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useDestinationList } from "hooks/services/useDestinationHook";
import { useGetSource } from "hooks/services/useSourceHook";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";

import SourceConnectionTable from "./components/SourceConnectionTable";
import SourceSettings from "./components/SourceSettings";
import { DropdownMenuOptionType } from "../../../../components/ui/DropdownMenu";
import { RoutePaths } from "../../../routePaths";

const SourceItemPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.SOURCE_ITEM);
  const params = useParams<{ "*": StepsTypes | "" | undefined; id: string }>();
  const navigate = useNavigate();
  const { formatMessage } = useIntl();
  const currentStep = useMemo<StepsTypes | "" | undefined>(
    () => (params["*"] === "" ? StepsTypes.OVERVIEW : params["*"]),
    [params]
  );

  const source = useGetSource(params.id || "");
  const sourceDefinition = useSourceDefinition(source.sourceDefinitionId);

  // We load only connections attached to this source to be shown in the connections grid
  const { connections } = useConnectionList({ sourceId: [source.sourceId] });

  const breadcrumbsData = [
    {
      label: formatMessage({ id: "sidebar.sources" }),
      to: "..",
    },
    { label: source.name },
  ];

  // We load all destinations so the add destination button has a pre-filled list of options.
  const { destinations } = useDestinationList();
  const destinationDropdownOptions: DropdownMenuOptionType[] = useMemo(
    () =>
      destinations.map((destination) => {
        return {
          as: "button",
          icon: <ConnectorIcon icon={destination.icon} />,
          iconPosition: "right",
          displayName: destination.name,
          value: destination.destinationId,
        };
      }),
    [destinations]
  );

  const onSelectStep = (id: string) => {
    const path = id === StepsTypes.OVERVIEW ? "." : id.toLowerCase();
    navigate(path);
  };

  const onSelect = (data: DropdownMenuOptionType) => {
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
              element={<SourceSettings currentSource={source} connectionsWithSource={connections} />}
            />
            <Route
              index
              element={
                <>
                  <TableItemTitle
                    type="destination"
                    dropdownOptions={destinationDropdownOptions}
                    onSelect={onSelect}
                    entity={source.sourceName}
                    entityName={source.name}
                    entityIcon={source.icon}
                    releaseStage={sourceDefinition.releaseStage}
                  />
                  {connections.length ? (
                    <SourceConnectionTable connections={connections} />
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
