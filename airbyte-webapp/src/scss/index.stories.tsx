import { ComponentStory, ComponentMeta } from "@storybook/react";

import { classy } from "utils/components";

const Div = classy("div", "with-text-styles");

export default {
  title: "Styles/Text",
  component: Div,
  argTypes: {},
} as ComponentMeta<typeof Div>;

const Template: ComponentStory<typeof Div> = ({ children }) => (
  <Div>
    <h1>H1 {children}</h1>
    <h2>H2 {children}</h2>
    <h3>H3 {children}</h3>
    <h4>H4 {children}</h4>
    <p className="txt-1">.txt-1 {children}</p>
    <p className="txt-2">.txt-2 {children}</p>
    <p className="txt-info">.txt-info {children}</p>
    <p className="txt-billing-line">.txt-billing-line {children}</p>
  </Div>
);

export const Primary = Template.bind({});
Primary.args = {
  children: "The quick brown fox jumped over the lazy dog.",
};
