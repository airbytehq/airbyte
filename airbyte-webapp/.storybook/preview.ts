import { addDecorator } from "@storybook/react";

import { withProviders } from "./withProvider";
import '!style-loader!css-loader!sass-loader!../src/scss/global.scss';

addDecorator(withProviders);

export const parameters = {};
