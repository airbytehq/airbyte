import { addDecorator } from "@storybook/react";

import { withProviders } from "./withProvider";

import "!style-loader!css-loader!sass-loader!../public/index.css";

addDecorator(withProviders);

export const parameters = {};
