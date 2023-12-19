import React from "react";
// Import the original mapper
import MDXComponents from "@theme-original/MDXComponents";
import { AppliesTo } from "@site/src/components/AppliesTo";
import { FieldAnchor } from "@site/src/components/FieldAnchor";
import { HideInUI } from "@site/src/components/HideInUI";
import { HeaderDecoration } from "@site/src/components/HeaderDecoration";
import { FlavorInformation } from "@site/src/components/FlavorInformation";

export default {
  // Re-use the default mapping
  ...MDXComponents,
  AppliesTo,
  FieldAnchor,
  HideInUI,
  HeaderDecoration,
  FlavorInformation,
};
