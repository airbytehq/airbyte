import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Box, Typography } from "@mui/material";
import React, { Suspense, useCallback, useState } from "react";
import { FormattedMessage } from "react-intl";
import { Route, Routes, Navigate } from "react-router-dom";
import styled from "styled-components";

import { Button } from "components";
// import { Button, DropDownRow } from "components";
import ApiErrorBoundary from "components/ApiErrorBoundary";
import Breadcrumbs from "components/Breadcrumbs";
import { CreateStepTypes } from "components/ConnectionStep";
// import { TableItemTitle } from "components/ConnectorBlocks";
// import { ConnectorIcon } from "components/ConnectorIcon";
import DeleteBlock from "components/DeleteBlock";
import LoadingPage from "components/LoadingPage";
import { PageSize } from "components/PageSize";
import { Pagination } from "components/Pagination";
import { Separator } from "components/Separator";
import { CategoryItem } from "components/TabMenu";

import { SourceDefinitionRead } from "core/request/AirbyteClient";
import { FilterSourceItemRequestBody } from "core/request/DaspireClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
// import { useConnectionList } from "hooks/services/useConnectionHook";
import { usePageConfig } from "hooks/services/usePageConfig";
import { useGetSourceItem } from "hooks/services/useSourceHook";
import { useDeleteSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
// import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
// import { getIcon } from "utils/imageUtils";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";
import { ServiceFormValues } from "views/Connector/ServiceForm/types";
import TestConnection from "views/Connector/TestConnection";

import HeaderSction from "./components/HeaderSection";
import NewSourceConnectionTable from "./components/NewSourceConnectionTable";
import SourceSettings from "./components/SourceSettings";
// import { useDestinationList } from "../../../../hooks/services/useDestinationHook";
import { RoutePaths } from "../../../routePaths";

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
  display: flex;
  flex-direction: column;
`;

const TableContainer = styled.div`
  margin-right: 70px;
`;
const BtnIcon = styled(FontAwesomeIcon)`
  font-size: 16px;
  margin-right: 10px;
`;
const BtnInnerContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 8px 4px;
`;
const BtnText = styled.div`
  font-weight: 500;
  font-size: 16px;
  color: #ffffff;
`;
const Footer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
`;
const SourceItemPage: React.FC<SettingsPageProps> = ({ pageConfig: pageConfigs }) => {
  useTrackPage(PageTrackingCodes.SOURCE_ITEM);
  const { query, push, pathname } = useRouter();
  const [currentStep, setCurrentStep] = useState(StepsTypes.CREATE_ENTITY);
  const [loadingStatus, setLoadingStatus] = useState<boolean>(true);
  const [fetchingConnectorError, setFetchingConnectorError] = useState<JSX.Element | string | null>(null);
  const [pageConfig, updatePageSize] = usePageConfig();
  const [pageCurrent, setCurrentPageSize] = useState<number>(pageConfig?.sourceItem?.pageSize);
  const initialFiltersState = {
    sourceId: query.id,
    pageSize: pageCurrent,
    pageCurrent: query.pageCurrent ? JSON.parse(query.pageCurrent) : 1,
  };

  const [filters, setFilters] = useState<FilterSourceItemRequestBody>(initialFiltersState);
  const [sourceFormValues, setSourceFormValues] = useState<ServiceFormValues | null>({
    name: "",
    serviceType: "",
    connectionConfiguration: {},
  });

  // const source = useGetSource(query.id);

  const onSelectFilter = useCallback(
    (
      filterType: "pageCurrent" | "status" | "sourceDefinitionId" | "destinationDefinitionId" | "pageSize",
      filterValue: number | string
    ) => {
      if (
        filterType === "status" ||
        filterType === "sourceDefinitionId" ||
        filterType === "destinationDefinitionId" ||
        filterType === "pageSize"
      ) {
        setFilters({ ...filters, [filterType]: filterValue, pageCurrent: 1 });
      } else if (filterType === "pageCurrent") {
        setFilters({ ...filters, [filterType]: filterValue as number });
      }
    },
    [filters]
  );
  const onChangePageSize = useCallback(
    (size: number) => {
      setCurrentPageSize(size);
      updatePageSize("sourceItem", size);
      onSelectFilter("pageSize", size);
    },
    [onSelectFilter]
  );
  const { SourceRead, WebBackendConnectionReadList, total, pageSize } = useGetSourceItem(filters);

  // console.log(source, "Response");
  // console.log(source?.SourceRead?.sourceDefinitionId, "id");

  const sourceDefinition = useSourceDefinition(SourceRead?.sourceDefinitionId);

  // const { destinations } = useDestinationList();

  // const { destinationDefinitions } = useDestinationDefinitionList();

  // const { connections } = useConnectionList();

  const { mutateAsync: deleteSource } = useDeleteSource();

  const breadcrumbsData = [
    {
      name: <FormattedMessage id="tables.allSources" />,
      onClick: () => push(".."),
    },
    { name: SourceRead?.name },
  ];

  // const connectionsWithSource = connections?.filter(
  //   (connectionItem) => connectionItem?.sourceId === source?.SourceRead?.sourceId
  // );
  // console.log(connectionsWithSource, "ss");
  // const destinationsDropDownData = useMemo(
  //   () =>
  //     destinations.map((item) => {
  //       const destinationDef = destinationDefinitions.find(
  //         (dd) => dd.destinationDefinitionId === item.destinationDefinitionId
  //       );
  //       return {
  //         label: item.name,
  //         value: item.destinationId,
  //         img: <ConnectorIcon icon={destinationDef?.icon} />,
  //       };
  //     }),
  //   [destinations, destinationDefinitions]
  // );

  // const onSelect = (data: DropDownRow.IDataItem) => {
  //   if (data.value === "create-new-item") {
  //     push(`../${RoutePaths.SelectConnection}`, {
  //       state: { sourceId: source.sourceId, currentStep: CreateStepTypes.CREATE_DESTINATION },
  //     });
  //   } else {
  //     push(`../${RoutePaths.ConnectionNew}`, {
  //       state: { destinationId: data.value, sourceId: source.sourceId, currentStep: CreateStepTypes.CREATE_CONNECTION },
  //     });
  //   }
  // };

  const goBack = () => {
    push(`/${RoutePaths.Source}`);
  };

  // const onDelete = async () => {
  //   await deleteSource({ connectionsWithSource, source });
  // };
  const onDelete = async () => {
    await deleteSource({ source: SourceRead, connectionsWithSource: WebBackendConnectionReadList?.connections });
  };
  const menuItems: CategoryItem[] = pageConfigs?.menuConfig || [
    {
      routes: [
        {
          path: "overview",
          name: <FormattedMessage id="tables.overview" />,
          component: (
            <TableContainer>
              {WebBackendConnectionReadList?.connections?.length === 0 ? (
                <Typography
                  textAlign="left"
                  fontSize={{ lg: 24, md: 24, sm: 20, xs: 18 }}
                  color="#27272A"
                  fontWeight={500}
                >
                  0 Destinations
                </Typography>
              ) : null}
              <Box textAlign="right">
                {" "}
                <Button
                  size="lg"
                  onClick={() =>
                    push(`../${RoutePaths.SelectConnection}`, {
                      state: {
                        sourceId: SourceRead?.sourceId,
                        currentStep: CreateStepTypes.CREATE_DESTINATION,
                      },
                    })
                  }
                >
                  <BtnInnerContainer>
                    <BtnIcon icon={faPlus} />
                    <BtnText>
                      <FormattedMessage id="destinations.newDestinationTitle" />
                    </BtnText>
                  </BtnInnerContainer>
                </Button>
              </Box>
              {/* <TableItemTitle
                dropDownData={destinationsDropDownData}
                onSelect={onSelect}
                num={connectionsWithSource.length}
                btnText={<FormattedMessage id="destinations.newDestinationTitle" />}
                type="destination"
                entity={source.sourceName}
                entityName={source.name}
                entityIcon={sourceDefinition ? getIcon(sourceDefinition.icon) : null}
                releaseStage={sourceDefinition.releaseStage}
              /> */}
              {WebBackendConnectionReadList?.connections?.length > 0 && (
                <Box pt={2}>
                  <NewSourceConnectionTable connections={WebBackendConnectionReadList?.connections} />
                  <Separator height="24px" />
                  <Footer>
                    <PageSize currentPageSize={pageCurrent} totalPage={total / pageSize} onChange={onChangePageSize} />
                    <Pagination
                      pages={total / pageSize}
                      value={filters.pageCurrent}
                      onChange={(value: number) => onSelectFilter("pageCurrent", value)}
                    />
                  </Footer>
                  <Separator height="24px" />
                </Box>
              )}
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
                  currentSource={SourceRead}
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
      {currentStep === StepsTypes.TEST_CONNECTION && (
        <HeaderSction
          sourceDefinition={sourceDefinition as SourceDefinitionRead}
          data={menuItems}
          onSelect={onSelectMenuItem}
          activeItem={pathname}
        />
      )}
      <ConnectorDocumentationWrapper>
        {currentStep !== StepsTypes.TEST_CONNECTION && (
          <HeaderSction
            sourceDefinition={sourceDefinition as SourceDefinitionRead}
            data={menuItems}
            onSelect={onSelectMenuItem}
            activeItem={pathname}
          />
        )}
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
