import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Box } from "@mui/material";
import { useCallback, useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";

import { Button, DropDown, DropDownRow, NewMainPageWithScroll } from "components";
import { SortOrderEnum } from "components/EntityTable/types";
import HeadTitle from "components/HeadTitle";
import { PageSize } from "components/PageSize";
import PageTitle from "components/PageTitle";
import { Pagination } from "components/Pagination";
import { Separator } from "components/Separator";

import { FilterSourceRequestBody } from "core/request/DaspireClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
// import { useConnectionFilterOptions, useFilteredConnectionList } from "hooks/services/useConnectionHook";

import { useConnectionFilterOptions } from "hooks/services/useConnectionHook";
import { usePageConfig } from "hooks/services/usePageConfig";
import { usePaginatedSources } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import SourcesTable from "./components/SourcesTable";
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
const DDContainer = styled.div<{
  margin?: string;
}>`
  width: 195px;
  margin: ${({ margin }) => margin};
  margin-left: auto;
  margin-right: 32px;
`;

const AllSourcesPage: React.FC = () => {
  const { query } = useRouter();
  // const { push } = useRouter();
  const navigate = useNavigate();
  const [pageConfig, updatePageSize] = usePageConfig();
  // const [currentPageSize, setCurrentPageSize] = useState<number>(pageConfig.connection.pageSize);
  const [pageCurrent, setCurrentPageSize] = useState<number>(pageConfig?.source?.pageSize);
  // const { sources } = useSourceList();
  const [sortFieldName, setSortFieldName] = useState("");
  const [sortDirection, setSortDirection] = useState("");
  const [localSortOrder, setLocalSortOrder] = useState(SortOrderEnum.DESC);
  const [sourceSortOrder, setSourceSortOrder] = useState(SortOrderEnum.DESC);
  useEffect(() => {
    // Set initial sort order to DESC when the component mounts
    onSelectFilter("sortFieldName", "");
    setSourceSortOrder(SortOrderEnum.DESC);
    setLocalSortOrder(SortOrderEnum.DESC);
  }, []);
  useTrackPage(PageTrackingCodes.SOURCE_LIST);
  const workspace = useCurrentWorkspace();
  const { sourceOptions } = useConnectionFilterOptions(workspace.workspaceId);
  const initialFiltersState = {
    workspaceId: workspace.workspaceId,
    pageSize: pageCurrent,
    pageCurrent: query.pageCurrent ? JSON.parse(query.pageCurrent) : 1,
    SourceDefinitionId: sourceOptions[0].value,
    sortDetails: {
      sortFieldName,
      sortDirection,
    },
  };

  const [filters, setFilters] = useState<FilterSourceRequestBody>(initialFiltersState);
  const { sources, total, pageSize } = usePaginatedSources(filters);

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

  // const onSelectFilter = useCallback(
  //   (filterType: "pageCurrent" | "SourceDefinitionId" | "pageSize" | "sortDirection" | "sortFieldName", filterValue: number | string) => {
  //     if (filterType === "SourceDefinitionId" || filterType === "pageSize"|| filterType === "sortDirection" || filterType === "sortFieldName") {
  //       setFilters({ ...filters, [filterType]: filterValue, pageCurrent: 1 });
  //     } else if (filterType === "pageCurrent") {
  //       setFilters({ ...filters, [filterType]: filterValue as number });
  //     }
  //   },
  //   [filters,sortDirection,sortFieldName]
  // );
  const onSelectFilter = useCallback(
    (
      filterType: "pageCurrent" | "SourceDefinitionId" | "pageSize" | "sortDirection" | "sortFieldName",
      filterValue: number | string
    ) => {
      setFilters((prevFilters) => {
        if (filterType === "SourceDefinitionId" || filterType === "pageSize") {
          return { ...prevFilters, [filterType]: filterValue };
        } else if (filterType === "sortDirection" || filterType === "sortFieldName") {
          return {
            ...prevFilters,
            sortDetails: {
              ...prevFilters.sortDetails,
              [filterType]: filterValue,
            },
            pageCurrent: prevFilters.pageCurrent,
          };
        } else if (filterType === "pageCurrent") {
          setLocalSortOrder(SortOrderEnum.DESC);
          setSourceSortOrder(SortOrderEnum.DESC);
          return {
            ...filters,
            [filterType]: filterValue as number,
            sortDetails: { sortFieldName: "", sortDirection: "" },
          };
        }
        return prevFilters;
      });
    },
    []
  );
  const onChangePageSize = useCallback(
    (size: number) => {
      setCurrentPageSize(size);
      updatePageSize("source", size);
      onSelectFilter("pageSize", size);
    },
    [onSelectFilter]
  );

  // const onCreateSource = () => push(`${RoutePaths.SelectSource}`);

  return (
    <>
      {sources && sources?.length > 0 ? (
        <NewMainPageWithScroll
          headTitle={<HeadTitle titles={[{ id: "admin.sources" }]} />}
          pageTitle={
            <PageTitle
              withPadding
              title=""
              endComponent={
                <Button onClick={() => navigate(`${RoutePaths.SelectSource}`)} data-id="new-source">
                  <BtnInnerContainer>
                    <BtnIcon icon={faPlus} />
                    <BtnText>
                      <FormattedMessage id="sources.newSource" />
                    </BtnText>
                  </BtnInnerContainer>
                </Button>
              }
            />
          }
        >
          <DDContainer>
            <DropDown
              $withBorder
              $background="white"
              value={filters.SourceDefinitionId}
              options={sourceOptions}
              onChange={(option: DropDownRow.IDataItem) => onSelectFilter("SourceDefinitionId", option.value)}
            />
          </DDContainer>
          <Separator height="10px" />
          <SourcesTable
            sources={sources}
            setSortFieldName={setSortFieldName}
            setSortDirection={setSortDirection}
            onSelectFilter={onSelectFilter}
            localSortOrder={localSortOrder}
            setLocalSortOrder={setLocalSortOrder}
            sourceSortOrder={sourceSortOrder}
            setSourceSortOrder={setSourceSortOrder}
          />
          <Separator height="24px" />
          <Footer>
            <PageSize currentPageSize={pageCurrent} totalPage={total / pageSize} onChange={onChangePageSize} />
            <Box paddingLeft="20px">
              <Pagination
                pages={total / pageSize}
                value={filters.pageCurrent}
                onChange={(value: number) => onSelectFilter("pageCurrent", value)}
              />
            </Box>
          </Footer>
          <Separator height="24px" />
        </NewMainPageWithScroll>
      ) : (
        navigate(`${RoutePaths.SelectSource}`)
      )}
    </>
  );
};

export default AllSourcesPage;
