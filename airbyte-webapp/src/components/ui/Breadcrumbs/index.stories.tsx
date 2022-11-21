import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Breadcrumbs, BreadcrumbsDataItem } from "./Breadcrumbs";

export default {
  title: "UI/Breadcrumbs",
  component: Breadcrumbs,
  argTypes: {},
} as ComponentMeta<typeof Breadcrumbs>;

const Template: ComponentStory<typeof Breadcrumbs> = (args) => <Breadcrumbs {...args} />;

const data: BreadcrumbsDataItem[] = [
  {
    label: "Workspace",
    to: "/workspace",
  },
  {
    label: "Source",
    to: "/workspace/source",
  },
  {
    label: "Settings",
  },
];

export const Primary = Template.bind({});
Primary.args = {
  data,
};
