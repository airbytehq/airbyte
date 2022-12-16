import { ComponentStory, ComponentMeta } from "@storybook/react";

import { BarChart } from "./BarChart";

export default {
  title: "UI/BarChart",
  component: BarChart,
  argTypes: {},
} as ComponentMeta<typeof BarChart>;

const Template: ComponentStory<typeof BarChart> = (args) => <BarChart {...args} />;

const data = [
  { name: "2017", value: 100 },
  { name: "2018", value: 300 },
  { name: "2019", value: 500 },
  { name: "2020", value: 400 },
  { name: "2021", value: 200 },
];
export const Primary = Template.bind({});
Primary.args = {
  data,
  legendLabels: ["value"],
  xLabel: "Year",
  yLabel: "Amount",
};
