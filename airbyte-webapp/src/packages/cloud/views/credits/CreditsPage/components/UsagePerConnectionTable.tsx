import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import queryString from "query-string";
import { CellProps } from "react-table";

import { CreditConsumptionByConnector } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import Table from "components/Table";
import { SortOrderEnum } from "components/EntityTable/types";
import SortButton from "components/EntityTable/components/SortButton";
import useRouter from "hooks/useRouter";
import ConnectionCell from "./ConnectionCell";
import UsageCell from "./UsageCell";

const Content = styled.div`
  padding: 0 60px 0 15px;
`;

type UsagePerConnectionTableProps = {
  creditConsumption: CreditConsumptionByConnector[];
};
const UsagePerConnectionTable: React.FC<UsagePerConnectionTableProps> = ({
  creditConsumption,
}) => {
  const { query, push } = useRouter();

  const creditConsumptionWithPercent = React.useMemo(() => {
    const sumCreditsConsumed = creditConsumption.reduce(
      (a, b) => a + b.creditsConsumed,
      0
    );
    return creditConsumption.map((item) => ({
      ...item,
      creditsConsumedPercent:
        item.creditsConsumed !== 0
          ? (item.creditsConsumed / sumCreditsConsumed) * 100
          : 0,
    }));
  }, [creditConsumption]);

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
          : `${a.sourceDefinitionName}${a.destinationDefinitionName}`
              .toLowerCase()
              .localeCompare(
                `${b.sourceDefinitionName}${b.destinationDefinitionName}`.toLowerCase()
              );

      if (sortOrder === SortOrderEnum.DESC) {
        return -1 * result;
      }

      return result;
    },
    [sortBy, sortOrder]
  );

  const sortingData = React.useMemo(
    () => creditConsumptionWithPercent.sort(sortData),
    [sortData, creditConsumptionWithPercent]
  );

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
        customWidth: 30,
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
        Cell: ({
          cell,
          row,
        }: CellProps<
          CreditConsumptionByConnector & { creditsConsumedPercent: number }
        >) => (
          <UsageCell
            value={cell.value}
            percent={row.original.creditsConsumedPercent}
          />
        ),
      },
      // TODO: Replace to Grow column
      {
        Header: "",
        accessor: "connectionId",
        Cell: <div />,
        customWidth: 20,
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
