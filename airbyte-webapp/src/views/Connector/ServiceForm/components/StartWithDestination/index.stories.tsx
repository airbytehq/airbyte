import { ComponentMeta, ComponentStory } from "@storybook/react";
import { Formik } from "formik";

import { mockData } from "../../../../../test-utils/mock-data/mockStartWithDestination";
import { StartWithDestination } from "./StartWithDestination";

export default {
  title: "Views/StartWithDestination",
  component: StartWithDestination,
  args: {
    destination: mockData,
    onDestinationSelect: () => {
      return undefined;
    },
  },
} as ComponentMeta<typeof StartWithDestination>;

export const Template: ComponentStory<typeof StartWithDestination> = (args) => (
  <Formik
    initialValues={{}}
    onSubmit={() => {
      return undefined;
    }}
  >
    <div style={{ maxWidth: 560 }}>
      <StartWithDestination {...args} />
    </div>
  </Formik>
);
