import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import queryString from "query-string";
import { CellProps } from "react-table";

import Table from "components/Table";
import { SortOrderEnum } from "components/EntityTable/types";
import SortButton from "components/EntityTable/components/SortButton";
import useRouter from "hooks/useRouter";
import ConnectionCell from "./ConnectionCell";
import { CreditConsumptionByConnector } from "packages/cloud/lib/domain/cloudWorkspaces/types";

const Content = styled.div`
  padding: 0 60px 0 15px;
`;

type UsagePerConnectionTableProps = {
  creditConsumption: { connectionId: string; creditsConsumed: number }[];
};
const UsagePerConnectionTable: React.FC<UsagePerConnectionTableProps> = ({
  creditConsumption,
}) => {
  const { query, push } = useRouter();

  const sortBy = query.sortBy || "connection";
  const sortOrder = query.order || SortOrderEnum.ASC;

  const onSortClick = useCallback(
    (field: string) => {
      const order =
        sortBy !== field
          ? SortOrderEnum.ASC
          : sortOrder === SortOrderEnum.ASC
          ? SortOrderEnum.DESC
          : SortOrderEnum.ASC;
      push({
        search: queryString.stringify(
          {
            sortBy: field,
            order: order,
          },
          { skipNull: true }
        ),
      });
    },
    [push, sortBy, sortOrder]
  );

  const sortData = useCallback(
    (a, b) => {
      const result =
        sortBy === "usage"
          ? a.creditsConsumed - b.creditsConsumed
          : a.connectionId
              .toLowerCase()
              .localeCompare(b.connectionId.toLowerCase());

      if (sortOrder === SortOrderEnum.DESC) {
        return -1 * result;
      }

      return result;
    },
    [sortBy, sortOrder]
  );

  const sortingData = React.useMemo(() => creditConsumption.sort(sortData), [
    sortData,
    creditConsumption,
  ]);

  const columns = React.useMemo(
    () => [
      {
        Header: (
          <>
            <FormattedMessage id="credits.connection" />
            <SortButton
              wasActive={sortBy === "connection"}
              lowToLarge={sortOrder === SortOrderEnum.ASC}
              onClick={() => onSortClick("connection")}
            />
          </>
        ),
        customWidth: 40,
        accessor: "sourceDefinitionName",
        Cell: ({ cell, row }: CellProps<CreditConsumptionByConnector>) => (
          <ConnectionCell
            sourceDefinitionName={cell.value}
            sourceDefinitionId={row.original.sourceDefinitionId}
            destinationDefinitionName={row.original.destinationDefinitionName}
            destinationDefinitionId={row.original.destinationDefinitionId}
          />
        ),
      },
      {
        Header: (
          <>
            <FormattedMessage id="credits.usage" />
            <SortButton
              wasActive={sortBy === "usage"}
              lowToLarge={sortOrder === SortOrderEnum.ASC}
              onClick={() => onSortClick("usage")}
            />
          </>
        ),
        accessor: "creditsConsumed",
      },
    ],
    [onSortClick, sortBy, sortOrder]
  );

  return (
    <Content>
      <Table columns={columns} data={sortingData} light />
    </Content>
  );
};

export default UsagePerConnectionTable;
