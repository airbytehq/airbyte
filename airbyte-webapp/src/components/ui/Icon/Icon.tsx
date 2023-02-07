import React from "react";

import { IconProps, Icons } from "./types";

export const Icon: React.FC<IconProps> = React.memo(({ type, ...props }) => {
  return React.createElement(Icons[type], {
    ...props,
  });
});
