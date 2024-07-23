// Import the original mapper
import { AppliesTo } from "@site/src/components/AppliesTo";
import { Arcade } from "@site/src/components/Arcade";
import { FieldAnchor } from "@site/src/components/FieldAnchor";
import { HeaderDecoration } from "@site/src/components/HeaderDecoration";
import { HideInUI } from "@site/src/components/HideInUI";
import { ProductInformation } from "@site/src/components/ProductInformation";
import { PyAirbyteExample } from "@site/src/components/PyAirbyteExample";
import { SpecSchema } from "@site/src/components/SpecSchema";
import MDXComponents from "@theme-original/MDXComponents";
import { Details } from "../../components/Details";

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
  Details,
};
