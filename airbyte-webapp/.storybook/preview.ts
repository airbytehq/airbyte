import { addDecorator } from "@storybook/react";

import { withProviders } from "./withProvider";

addDecorator(withProviders);

export const parameters = {};
