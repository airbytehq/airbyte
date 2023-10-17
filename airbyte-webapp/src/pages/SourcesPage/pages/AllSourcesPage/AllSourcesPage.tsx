import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
// import { useCallback, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, MainPageWithScroll } from "components";
import HeadTitle from "components/HeadTitle";
import PageTitle from "components/PageTitle";

// import { FilterSourceRequestBody } from "core/request/DaspireClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
// import { useConnectionFilterOptions, useFilteredConnectionList } from "hooks/services/useConnectionHook";
// import { usePageConfig } from "hooks/services/usePageConfig";
import { useSourceList } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
// import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import SourcesTable from "./components/SourcesTable";
import { RoutePaths } from "../../../routePaths";
// import { Separator } from "components/Separator";
// import { PageSize } from "components/PageSize";
// import { Separator } from "components/Separator";
// import { PageSize } from "components/PageSize";

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

const AllSourcesPage: React.FC = () => {
  // const { push, query } = useRouter();
  const { push } = useRouter();
  // const [pageConfig, updatePageSize] = usePageConfig();

  // const [currentPageSize, setCurrentPageSize] = useState<number>(pageConfig.connection.pageSize);
  // const [pageCurrent, setCurrentPageSize] = useState<number>(pageConfig.source.pageSize);
  const { sources } = useSourceList();

  useTrackPage(PageTrackingCodes.SOURCE_LIST);
  // const workspace = useCurrentWorkspace();
  // const initialFiltersState = {
  //   workspaceId: "fbc7e2ed-7d9c-459e-9831-26ce863f7b93",
  //   pageSize: pageCurrent,
  //   pageCurrent: query.pageCurrent ? JSON.parse(query.pageCurrent) : 1,
  // };

  // const [filters, setFilters] = useState<FilterSourceRequestBody>(initialFiltersState);
  // const { sources, total, pageSize } = usePaginatedSources(filters);
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
  //   (
  //     filterType: "pageCurrent" | "status" | "sourceDefinitionId" | "destinationDefinitionId" | "pageSize",
  //     filterValue: number | string
  //   ) => {
  //     if (
  //       filterType === "status" ||
  //       filterType === "sourceDefinitionId" ||
  //       filterType === "destinationDefinitionId" ||
  //       filterType === "pageSize"
  //     ) {
  //       setFilters({ ...filters, [filterType]: filterValue, pageCurrent: 1 });
  //     } else if (filterType === "pageCurrent") {
  //       setFilters({ ...filters, [filterType]: filterValue as number });
  //     }
  //   },
  //   [filters]
  // );
  // const onChangePageSize = useCallback(
  //   (size: number) => {
  //     setCurrentPageSize(size);
  //     updatePageSize("source", size);
  //     onSelectFilter("pageSize", size);
  //   },
  //   [onSelectFilter]
  // );
  const onCreateSource = () => push(`${RoutePaths.SelectSource}`);

  if (sources.length === 0) {
    onCreateSource();
    return null;
  }
  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "admin.sources" }]} />}
      pageTitle={
        <PageTitle
          withPadding
          title=""
          endComponent={
            <Button onClick={onCreateSource} data-id="new-source">
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
      {/* <Separator height="10px" />
      <PageSize currentPageSize={pageCurrent} totalPage={total / pageSize} onChange={onChangePageSize} />
      <Separator height="10px" /> */}
      <SourcesTable sources={sources} />
    </MainPageWithScroll>
  );
};

export default AllSourcesPage;
