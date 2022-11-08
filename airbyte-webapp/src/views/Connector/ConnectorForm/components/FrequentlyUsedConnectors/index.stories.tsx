import { ComponentStory, ComponentMeta } from "@storybook/react";
import { mockDestinationsData, mockSourcesData } from "test-utils/mock-data/mockFrequentlyUsedDestinations";

import { FrequentlyUsedConnectorsCard } from "./FrequentlyUsedConnectorsCard";

export default {
  title: "Views/FrequentlyUsedConnectors",
  component: FrequentlyUsedConnectorsCard,
  args: {
    connectors: mockDestinationsData,
    connectorType: "destination",
  },
} as ComponentMeta<typeof FrequentlyUsedConnectorsCard>;

const Template: ComponentStory<typeof FrequentlyUsedConnectorsCard> = (args) => (
  <div style={{ maxWidth: 560 }}>
    <FrequentlyUsedConnectorsCard {...args} />
  </div>
);
export const Destinations = Template.bind({});

export const Sources = Template.bind({});
Sources.args = {
  ...Template.args,
  connectors: mockSourcesData,
  connectorType: "source",
};
