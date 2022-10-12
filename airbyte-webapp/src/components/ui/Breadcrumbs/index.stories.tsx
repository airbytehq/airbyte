import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Breadcrumbs, BreadcrumbsDataItem } from "./Breadcrumbs";

export default {
  title: "UI/Breadcrumbs",
  component: Breadcrumbs,
  argTypes: {},
} as ComponentMeta<typeof Breadcrumbs>;

const Template: ComponentStory<typeof Breadcrumbs> = (args) => <Breadcrumbs {...args} />;

const onClick = () => {
  console.log("onClick");
};

const data: BreadcrumbsDataItem[] = [
  {
    name: "Workspace",
    onClick,
  },
  {
    name: "Source",
    onClick,
  },
  {
    name: "Settings",
    onClick,
  },
];

export const Primary = Template.bind({});
Primary.args = {
  data,
};
