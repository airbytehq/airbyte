import { ComponentStory, ComponentMeta } from "@storybook/react";

import { CategoryItem, SideMenu } from "./SideMenu";

export default {
  title: "UI/SideMenu",
  component: SideMenu,
  argTypes: {},
} as ComponentMeta<typeof SideMenu>;

const Template: ComponentStory<typeof SideMenu> = (args) => <SideMenu {...args} />;

const data: CategoryItem[] = [
  {
    routes: [
      {
        path: "account",
        name: "Account",
        component: () => <>This is the account page</>,
      },
      {
        path: `sources`,
        name: "Sources",
        indicatorCount: 7,
        component: () => <>This is the sources page</>,
      },
      {
        path: `destinations`,
        name: "Destinations",
        indicatorCount: 1,
        component: () => <>This is the destinations page</>,
      },
    ],
  },
  {
    category: "Other Stuff",
    routes: [
      {
        path: "notifications",
        name: "Notifications",
        component: () => <>This is the notifications page</>,
      },
    ],
  },
];

export const Primary = Template.bind({});
Primary.args = {
  data,
  activeItem: "sources",
  onSelect: () => {
    console.log("onSelect");
  },
};
