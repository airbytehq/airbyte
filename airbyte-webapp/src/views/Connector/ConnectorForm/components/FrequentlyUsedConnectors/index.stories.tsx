import { ComponentStory, ComponentMeta } from "@storybook/react";

import { mockData } from "../../../../../test-utils/mock-data/mockFrequentlyUsedDestinations";
import { FrequentlyUsedConnectorsCard } from "./FrequentlyUsedConnectorsCard";

export default {
  title: "Views/FrequentlyUsedConnectors",
  component: FrequentlyUsedConnectorsCard,
  args: {
    destinations: mockData,
    propertyPath: "serviceType",
  },
} as ComponentMeta<typeof FrequentlyUsedConnectorsCard>;

export const Template: ComponentStory<typeof FrequentlyUsedConnectorsCard> = (args) => (
  <div style={{ maxWidth: 560 }}>
    <FrequentlyUsedConnectorsCard {...args} />
  </div>
);
