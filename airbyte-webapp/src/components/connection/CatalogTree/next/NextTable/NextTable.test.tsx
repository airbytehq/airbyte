import { render } from "@testing-library/react";
import { CellProps } from "react-table";

import { NextTable } from "./NextTable";

interface Item {
  name: string;
  value: number;
}

describe("<NextTable>", () => {
  it("should should render the table with passed data", () => {
    const data: Item[] = [
      { name: "2017", value: 100 },
      { name: "2018", value: 300 },
      { name: "2019", value: 500 },
      { name: "2020", value: 400 },
      { name: "2021", value: 200 },
    ];

    const columns = [
      {
        Header: "Name",
        accessor: "name",
        Cell: ({ cell }: CellProps<Item>) => <strong>{cell.value}</strong>,
      },
      {
        Header: "Value",
        accessor: "value",
        Cell: ({ cell }: CellProps<Item>) => <>{cell.value}</>,
      },
    ];

    const { getByText, container } = render(<NextTable columns={columns} data={data} />);
    expect(getByText(/2019/)).toBeInTheDocument();
    expect(getByText(/500/)).toBeInTheDocument();

    expect(container.querySelectorAll("thead tr")).toHaveLength(1);
    expect(container.querySelectorAll("tbody tr")).toHaveLength(data.length);
  });
});
