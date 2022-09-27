import { ComponentStory, ComponentMeta } from "@storybook/react";
import { CellProps } from "react-table";

import { Table } from "./Table";

export default {
  title: "UI/Table",
  component: Table,
  argTypes: {},
} as ComponentMeta<typeof Table>;

const Template: ComponentStory<typeof Table> = (args) => <Table {...args} />;

interface Item {
  name: string;
  value: number;
}

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

export const Primary = Template.bind({});
Primary.args = {
  data,
  columns,
};
