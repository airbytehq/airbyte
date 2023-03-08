import React, { Suspense, useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import { Route, Routes, Navigate } from "react-router-dom";
import styled from "styled-components";

import { DropDownRow } from "components";
import ApiErrorBoundary from "components/ApiErrorBoundary";
import Breadcrumbs from "components/Breadcrumbs";
import { CreateStepTypes } from "components/ConnectionStep";
import { TableItemTitle, DefinitioDetails } from "components/ConnectorBlocks";
import { ConnectorIcon } from "components/ConnectorIcon";
import DeleteBlock from "components/DeleteBlock";
import LoadingPage from "components/LoadingPage";
import { TabMenu, CategoryItem } from "components/TabMenu";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useGetSource } from "hooks/services/useSourceHook";
import { useDeleteSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { getIcon } from "utils/imageUtils";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";
import { ServiceFormValues } from "views/Connector/ServiceForm/types";
import TestConnection from "views/Connector/TestConnection";

import { useDestinationList } from "../../../../hooks/services/useDestinationHook";
import { RoutePaths } from "../../../routePaths";
import SourceConnectionTable from "./components/SourceConnectionTable";
import SourceSettings from "./components/SourceSettings";

interface PageConfig {
  menuConfig: CategoryItem[];
}

interface SettingsPageProps {
  pageConfig?: PageConfig;
}

enum StepsTypes {
  CREATE_ENTITY = "createEntity",
  TEST_CONNECTION = "testConnection",
}

const Container = styled.div`
  padding: 0px 0px 0px 70px;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
`;

const TabContainer = styled.div`
  margin: 20px 20px 40px 0;
`;

const TableContainer = styled.div`
  margin-right: 70px;
`;

const SourceItemPage: React.FC<SettingsPageProps> = ({ pageConfig }) => {
  useTrackPage(PageTrackingCodes.SOURCE_ITEM);
  const { query, push, pathname } = useRouter<{ id: string }, { id: string; "*": string }>(); // params
  // const currentStep = useMemo<string>(() => (params["*"] === "" ? StepsTypes.OVERVIEW : params["*"]), [params]);
  const [currentStep, setCurrentStep] = useState(StepsTypes.CREATE_ENTITY);
  const [loadingStatus, setLoadingStatus] = useState<boolean>(true);
  const [fetchingConnectorError, setFetchingConnectorError] = useState<JSX.Element | string | null>(null);
  const [sourceFormValues, setSourceFormValues] = useState<ServiceFormValues | null>({
    name: "",
    serviceType: "",
    connectionConfiguration: {},
  });

  const source = useGetSource(query.id);
  const sourceDefinition = useSourceDefinition(source?.sourceDefinitionId);

  const { destinations } = useDestinationList();

  const { destinationDefinitions } = useDestinationDefinitionList();

  const { connections } = useConnectionList();
  const { mutateAsync: deleteSource } = useDeleteSource();

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="tables.allSources" />,
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

  // const onSelectStep = (id: string) => {
  //   const path = id === StepsTypes.OVERVIEW ? "." : id.toLowerCase();
  //   push(path);
  // };

  const onSelect = (data: DropDownRow.IDataItem) => {
    if (data.value === "create-new-item") {
      push(`../${RoutePaths.SelectConnection}`, {
        state: { sourceId: source.sourceId, currentStep: CreateStepTypes.CREATE_DESTINATION },
      });
    } else {
      push(`../${RoutePaths.ConnectionNew}`, {
        state: { destinationId: data.value, sourceId: source.sourceId, currentStep: CreateStepTypes.CREATE_CONNECTION },
      });
    }

    // const path = `../${RoutePaths.ConnectionNew}`;
    // const path = `/${RoutePaths.Connections}/${RoutePaths.ConnectionNew}`;
    // const state =
    //   data.value === "create-new-item"
    //     ?
    //     : {
    //         destinationId: data.value,
    //         sourceId: source.sourceId,
    //         currentStep: CreateStepTypes.CREATE_CONNECTION,
    //       };

    // push(path, { state });
  };

  const goBack = () => {
    push(`/${RoutePaths.Source}`);
  };

  const onDelete = async () => {
    await deleteSource({ connectionsWithSource, source });
  };

  // const onCreateClick = () => {
  //   push(`/${RoutePaths.Destination}/${RoutePaths.SelectDestination}`);
  // };

  const menuItems: CategoryItem[] = pageConfig?.menuConfig || [
    {
      routes: [
        {
          path: "overview",
          name: <FormattedMessage id="tables.overview" />,
          component: (
            <TableContainer>
              <TableItemTitle
                dropDownData={destinationsDropDownData}
                // onClick={onCreateClick}
                onSelect={onSelect}
                // type="source"
                num={connectionsWithSource.length}
                btnText={<FormattedMessage id="destinations.newDestinationTitle" />}
                type="destination"
                entity={source.sourceName}
                entityName={source.name}
                entityIcon={sourceDefinition ? getIcon(sourceDefinition.icon) : null}
                releaseStage={sourceDefinition.releaseStage}
              />
              {connectionsWithSource.length > 0 && <SourceConnectionTable connections={connectionsWithSource} />}
            </TableContainer>
          ),
          show: true,
        },
        {
          path: "settings",
          name: <FormattedMessage id="tables.settings" />,
          component: (
            <>
              {currentStep === StepsTypes.TEST_CONNECTION && (
                <TestConnection
                  isLoading={loadingStatus}
                  type="source"
                  onBack={() => {
                    setCurrentStep(StepsTypes.CREATE_ENTITY);
                  }}
                  onFinish={goBack}
                />
              )}
              {currentStep === StepsTypes.CREATE_ENTITY && (
                <SourceSettings
                  currentSource={source}
                  errorMessage={fetchingConnectorError}
                  onBack={goBack}
                  formValues={sourceFormValues}
                  afterSubmit={() => {
                    setLoadingStatus(false);
                  }}
                  onShowLoading={(
                    isLoading: boolean,
                    formValues: ServiceFormValues | null,
                    error: JSX.Element | string | null
                  ) => {
                    setSourceFormValues(formValues);
                    if (isLoading) {
                      setCurrentStep(StepsTypes.TEST_CONNECTION);
                      setLoadingStatus(true);
                    } else {
                      setCurrentStep(StepsTypes.CREATE_ENTITY);
                      setFetchingConnectorError(error);
                    }
                  }}
                />
              )}
            </>
          ),
          show: true,
        },
        {
          path: "danger-zone",
          name: <FormattedMessage id="tables.dangerZone" />,
          component: <DeleteBlock type="source" onDelete={onDelete} />,
          show: true,
        },
      ],
    },
  ];

  const onSelectMenuItem = (newPath: string) => {
    push(newPath);
  };

  const firstRoute = (): string => {
    const { routes } = menuItems[0];
    const filteredRoutes = routes.filter((route) => route.show === true);
    if (filteredRoutes.length > 0) {
      return filteredRoutes[0]?.path;
    }
    return "";
  };

  return (
    <Container>
      <Breadcrumbs data={breadcrumbsData} currentStep={0} />
      <ConnectorDocumentationWrapper>
        <DefinitioDetails name={sourceDefinition.name} icon={sourceDefinition.icon} type="source" />
        <TabContainer>
          <TabMenu data={menuItems} onSelect={onSelectMenuItem} activeItem={pathname} size="16" lastOne />
        </TabContainer>
        <ApiErrorBoundary>
          <Suspense fallback={<LoadingPage />}>
            <Routes>
              {menuItems
                .flatMap((menuItem) => menuItem.routes)
                .map(
                  ({ path, component: Component, show }) => show && <Route key={path} path={path} element={Component} />
                )}
              <Route path="*" element={<Navigate to={firstRoute()} replace />} />
            </Routes>
          </Suspense>
        </ApiErrorBoundary>
      </ConnectorDocumentationWrapper>
    </Container>
  );
};

export default SourceItemPage;
