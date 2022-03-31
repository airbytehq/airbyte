import { addDecorator } from "@storybook/react";

import { withProviders } from "./withProvider";
import { MockDecorator } from "./restHooksDecorator";

addDecorator(withProviders);
addDecorator(MockDecorator);

export const parameters = {};
