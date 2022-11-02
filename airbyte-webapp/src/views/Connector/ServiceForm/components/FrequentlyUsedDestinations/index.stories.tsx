import { ComponentStory, ComponentMeta } from "@storybook/react";

import { mockData } from "../../../../../test-utils/mock-data/mockFrequentlyUsedDestinations";
import { FrequentlyUsedDestinationsCard } from "./FrequentlyUsedDestinationsCard";

export default {
  title: "Views/FrequentlyUsedDestinations",
  component: FrequentlyUsedDestinationsCard,
  args: {
    destinations: mockData,
    propertyPath: "serviceType",
  },
} as ComponentMeta<typeof FrequentlyUsedDestinationsCard>;

export const Template: ComponentStory<typeof FrequentlyUsedDestinationsCard> = (args) => (
  <div style={{ maxWidth: 560 }}>
    <FrequentlyUsedDestinationsCard {...args} />
  </div>
);
