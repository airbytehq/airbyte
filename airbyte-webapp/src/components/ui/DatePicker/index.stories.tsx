import { ComponentStory, ComponentMeta } from "@storybook/react";
import { useState } from "react";

import { DatePicker } from "./DatePicker";

export default {
  title: "Ui/DatePicker",
  component: DatePicker,
  argTypes: {
    onChange: { action: "changed" },
  },
} as ComponentMeta<typeof DatePicker>;

// Note: storybook
const Template: ComponentStory<typeof DatePicker> = (args) => {
  const [value, setValue] = useState("");

  return (
    <DatePicker
      {...args}
      value={value}
      onChange={(value) => {
        args.onChange(value);
        setValue(value);
      }}
      key="static"
    />
  );
};

export const YearMonthDay = Template.bind({});
YearMonthDay.args = {
  placeholder: "YYYY-MM-DD",
};

export const UtcTimestamp = Template.bind({});
UtcTimestamp.args = {
  placeholder: "YYYY-MM-DDTHH:mm:ssZ",
  withTime: true,
};
