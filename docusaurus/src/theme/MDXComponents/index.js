import React from "react";
// Import the original mapper
import MDXComponents from "@theme-original/MDXComponents";
import { AppliesTo } from "@site/src/components/AppliesTo";
import { FieldAnchor } from "@site/src/components/FieldAnchor";
import { HideInUI } from "@site/src/components/HideInUI";
import { HeaderDecoration } from "@site/src/components/HeaderDecoration";
import { SpecSchema } from "@site/src/components/SpecSchema";
import { PyAirbyteExample } from "@site/src/components/PyAirbyteExample";
import { ProductInformation } from "@site/src/components/ProductInformation";
import { Arcade } from "@site/src/components/Arcade";

export default {
  // Re-use the default mapping
  ...MDXComponents,
  Arcade,
  AppliesTo,
  FieldAnchor,
  HideInUI,
  HeaderDecoration,
  SpecSchema,
  PyAirbyteExample,
  ProductInformation,
};
