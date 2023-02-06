import { ComponentMeta, Story } from "@storybook/react";
import { createColumnHelper } from "@tanstack/react-table";

import { NextTable, TableProps } from "./NextTable";

interface Item {
  name: string;
  value: number;
}

export default {
  title: "UI/NextTable",
  component: NextTable,
  argTypes: {},
} as ComponentMeta<typeof NextTable>;

const Template =
  <T,>(): Story<TableProps<T>> =>
  (args) =>
    <NextTable<T> {...args} />;

const data: Item[] = [
  { name: "2017", value: 100 },
  { name: "2018", value: 300 },
  { name: "2019", value: 500 },
  { name: "2020", value: 400 },
  { name: "2021", value: 200 },
];

const columnHelper = createColumnHelper<Item>();

const columns = [
  columnHelper.accessor("name", {
    header: "Name",
    cell: ({ getValue }) => <strong>{getValue<string>()}</strong>,
  }),
  columnHelper.accessor("value", {
    header: "Value",
    cell: ({ getValue }) => getValue<string>(),
  }),
];

export const Primary = Template<Item>().bind({});
Primary.args = {
  data,
  columns,
};
