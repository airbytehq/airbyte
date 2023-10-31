import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState, useCallback } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, MainPageWithScroll } from "components";
import HeadTitle from "components/HeadTitle";
import { PageSize } from "components/PageSize";
import PageTitle from "components/PageTitle";
import { Pagination } from "components/Pagination";
import { Separator } from "components/Separator";

// import { FilterConnectionRequestBody } from "core/request/DaspireClient";
import { FilterDestinationRequestBody } from "core/request/DaspireClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
// import { useConnectionFilterOptions, useFilteredConnectionList } from "hooks/services/useConnectionHook";
import { usePaginatedDestination } from "hooks/services/useDestinationHook";
import { usePageConfig } from "hooks/services/usePageConfig";
import useRouter from "hooks/useRouter";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import DestinationsTable from "./components/DestinationsTable";
import { RoutePaths } from "../../../routePaths";

const BtnInnerContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 8px 4px;
`;

const BtnIcon = styled(FontAwesomeIcon)`
  font-size: 16px;
  margin-right: 10px;
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
  align-items: center;
  justify-content: center;
`;

const AllDestinationsPage: React.FC = () => {
  const { push, query } = useRouter();
  // const { push } = useRouter();
  // const { destinations } = useDestinationList();

  const [pageConfig, updatePageSize] = usePageConfig();
  // const [pageConfig] = usePageConfig();

  // const [currentPageSize] = useState<number>(pageConfig.connection.pageSize);
  const [pageCurrent, setCurrentPageSize] = useState<number>(pageConfig.connection.pageSize);
  useTrackPage(PageTrackingCodes.DESTINATION_LIST);
  const workspace = useCurrentWorkspace();
  const initialFiltersState = {
    workspaceId: workspace.workspaceId,
    pageSize: pageCurrent,
    pageCurrent: query.pageCurrent ? JSON.parse(query.pageCurrent) : 1,
  };

  const [filters, setFilters] = useState<FilterDestinationRequestBody>(initialFiltersState);
  const { destinations, total, pageSize } = usePaginatedDestination(filters);
  // const workspace = useCurrentWorkspace();
  // const { statusOptions, sourceOptions, destinationOptions } = useConnectionFilterOptions();

  // const initialFiltersState = {
  //   workspaceId: workspace.workspaceId,
  //   pageSize: currentPageSize,
  //   pageCurrent: query.pageCurrent ? JSON.parse(query.pageCurrent) : 1,
  //   status: statusOptions[0].value,
  //   sourceDefinitionId: sourceOptions[0].value,
  //   destinationDefinitionId: destinationOptions[0].value,
  // };

  // const [filters] = useState<FilterConnectionRequestBody>(initialFiltersState);
  // const [filters, setFilters] = useState<FilterConnectionRequestBody>(initialFiltersState);
  // const { connections, total, pageSize } = useFilteredConnectionList(filters);
  // const { connections } = useFilteredConnectionList(filters);
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
      updatePageSize("connection", size);
      onSelectFilter("pageSize", size);
    },
    [onSelectFilter]
  );
  const onCreateDestination = () => push(`${RoutePaths.SelectDestination}`);

  if (destinations.length === 0) {
    onCreateDestination();
    return null;
  }

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "admin.destinations" }]} />}
      pageTitle={
        <PageTitle
          withPadding
          title=""
          endComponent={
            <Button onClick={onCreateDestination} data-id="new-destination">
              <BtnInnerContainer>
                <BtnIcon icon={faPlus} />
                <BtnText>
                  <FormattedMessage id="destinations.newDestination" />
                </BtnText>
              </BtnInnerContainer>
            </Button>
          }
        />
      }
    >
      <Separator height="10px" />
      <DestinationsTable destinations={destinations} />
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
    </MainPageWithScroll>
  );
};

export default AllDestinationsPage;
