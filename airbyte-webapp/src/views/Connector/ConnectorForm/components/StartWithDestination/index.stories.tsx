import { ComponentMeta, ComponentStory } from "@storybook/react";

import { mockData } from "../../../../../test-utils/mock-data/mockStartWithDestination";
import { StartWithDestinationCard } from "./StartWithDestinationCard";

export default {
  title: "Views/StartWithDestination",
  component: StartWithDestinationCard,
  args: {
    destination: mockData,
    onDestinationSelect: () => {
      return undefined;
    },
  },
} as ComponentMeta<typeof StartWithDestinationCard>;

export const Template: ComponentStory<typeof StartWithDestinationCard> = (args) => (
  <div style={{ maxWidth: 560 }}>
    <StartWithDestinationCard {...args} />
  </div>
);
