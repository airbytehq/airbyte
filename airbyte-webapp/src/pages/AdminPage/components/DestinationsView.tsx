import React from "react";
import { FormattedMessage } from "react-intl";

import { Block, Title } from "./PageComponents";
import Table from "../../../components/Table";
import { CellProps } from "react-table";
import ConnectorCell from "./ConnectorCell";
import ImageCell from "./ImageCell";
import VersionCell from "./VersionCell";

const DestinationsView: React.FC = () => {
  const columns = React.useMemo(
    () => [
      {
        Header: <FormattedMessage id="admin.connectors" />,
        accessor: "connector",
        customWidth: 34,
        Cell: ({ cell }: CellProps<{}>) => (
          <ConnectorCell connectorName={cell.value} />
        )
      }
    ],
    []
  );
  const columnsCurrentDestination = React.useMemo(
    () => [
      ...columns,
      {
        Header: <FormattedMessage id="admin.codeSource" />,
        accessor: "image",
        customWidth: 36,
        Cell: ({ cell, row }: CellProps<{ imageLink: string }>) => (
          <ImageCell imageName={cell.value} link={row.original.imageLink} />
        )
      },
      {
        Header: <FormattedMessage id="admin.version" />,
        accessor: "version",
        collapse: true,
        Cell: ({ cell }: CellProps<{}>) => <VersionCell version={cell.value} />
      }
    ],
    [columns]
  );

  const columnsAllDestinations = React.useMemo(
    () => [
      ...columns,
      {
        Header: <FormattedMessage id="admin.image" />,
        accessor: "image",
        customWidth: 36,
        Cell: ({ cell, row }: CellProps<{ imageLink: string }>) => (
          <ImageCell imageName={cell.value} link={row.original.imageLink} />
        )
      },
      {
        Header: "",
        accessor: "version",
        collapse: true,
        Cell: () => <VersionCell empty />
      }
    ],
    [columns]
  );

  // TODO: add real data from BE
  const data = [
    {
      connector: "test",
      image: "image/test",
      imageLink: "https://github.com",
      version: "11.1"
    }
  ];

  return (
    <>
      <Block>
        <Title bold>
          <FormattedMessage id="admin.manageDestination" />
        </Title>
        <Table columns={columnsCurrentDestination} data={data} />
      </Block>

      <Block>
        <Title bold>
          <FormattedMessage id="admin.supportMultipleDestinations" />
        </Title>
        <Table columns={columnsAllDestinations} data={data} />
      </Block>
    </>
  );
};

export default DestinationsView;
