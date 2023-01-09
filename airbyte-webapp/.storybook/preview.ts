import { addDecorator } from "@storybook/react";

import { withProviders } from "./withProvider";

import "!style-loader!css-loader!sass-loader!../public/index.css";
import "../src/scss/global.scss";
import "../src/globals";

addDecorator(withProviders);

export const parameters = {};
