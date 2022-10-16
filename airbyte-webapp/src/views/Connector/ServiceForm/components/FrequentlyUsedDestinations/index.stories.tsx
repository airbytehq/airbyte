import { ComponentStory, ComponentMeta } from "@storybook/react";
import { Formik } from "formik";

import { mockData } from "../../../../../test-utils/mock-data/mockFrequentlyUsedDestinations";
import { FrequentlyUsedDestinations } from "./FrequentlyUsedDestinations";

export default {
  title: "Views/FrequentlyUsedDestinations",
  component: FrequentlyUsedDestinations,
  args: {
    destinations: mockData,
    propertyPath: "serviceType",
  },
} as ComponentMeta<typeof FrequentlyUsedDestinations>;

export const Template: ComponentStory<typeof FrequentlyUsedDestinations> = (args) => (
  <Formik
    initialValues={{ serviceType: "" }}
    onSubmit={() => {
      return undefined;
    }}
  >
    <div style={{ maxWidth: 560 }}>
      <FrequentlyUsedDestinations {...args} />
    </div>
  </Formik>
);
