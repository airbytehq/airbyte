import { ComponentStory, ComponentMeta } from "@storybook/react";

import { SlickSlider } from "./SlickSlider";

export default {
  title: "UI/SlickSlider",
  component: SlickSlider,
} as ComponentMeta<typeof SlickSlider>;

const cardStyle = {
  height: 100,
  border: "1px solid blue",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
};

export const Primary: ComponentStory<typeof SlickSlider> = (args) => (
  <div style={{ maxWidth: 560 }}>
    <SlickSlider {...args}>
      <div>
        <div style={cardStyle}>1</div>
      </div>
      <div>
        <div style={cardStyle}>2</div>
      </div>
      <div>
        <div style={cardStyle}>3</div>
      </div>
      <div>
        <div style={cardStyle}>4</div>
      </div>
      <div>
        <div style={cardStyle}>5</div>
      </div>
    </SlickSlider>
  </div>
);

export const WithTitle = Primary.bind({});
WithTitle.args = {
  title: "Test title text",
};
