// Import the original mapper
import { AgentConnectorTitle } from "@site/src/components/AgentConnectorTitle";
import { AppliesTo } from "@site/src/components/AppliesTo";
import { Arcade } from "@site/src/components/Arcade";
import { FieldAnchor } from "@site/src/components/FieldAnchor";
import { HeaderDecoration } from "@site/src/components/HeaderDecoration";
import { HideInUI } from "@site/src/components/HideInUI";
import { Navattic } from "@site/src/components/Navattic";
import { ProductInformation } from "@site/src/components/ProductInformation";
import { PyAirbyteExample } from "@site/src/components/PyAirbyteExample";
import { SpecSchema } from "@site/src/components/SpecSchema";
import MDXComponents from "@theme-original/MDXComponents";
import { CardWithIcon } from "../../components/Card/Card";
import { CopyPageButton } from "../../components/CopyPageButton/CopyPageButton";
import { Details } from "../../components/Details";
import { DocMetaTags } from "../../components/DocMetaTags";
import { EntityRelationshipDiagram } from "../../components/EntityRelationshipDiagram";
import { Grid } from "../../components/Grid/Grid";
import { YoutubeEmbed } from "../../components/YoutubeEmbed";

// Wrap API reference components with BrowserOnly to avoid SSR issues
// (they use @headlessui/react which causes "Passing props on Fragment" during SSG)
import BrowserOnly from "@docusaurus/BrowserOnly";

function SourceRequestSchema(props) {
  return (
    <BrowserOnly fallback={<div>Loading...</div>}>
      {() => {
        const { SourceRequestSchema: Component } = require("@site/src/components/SourceRequestSchema");
        return <Component {...props} />;
      }}
    </BrowserOnly>
  );
}

function SourceResponseSchema(props) {
  return (
    <BrowserOnly fallback={<div>Loading...</div>}>
      {() => {
        const { SourceResponseSchema: Component } = require("@site/src/components/SourceResponseSchema");
        return <Component {...props} />;
      }}
    </BrowserOnly>
  );
}

export default {
  // Re-use the default mapping
  ...MDXComponents,
  AgentConnectorTitle,
  Arcade,
  AppliesTo,
  FieldAnchor,
  HideInUI,
  HeaderDecoration,
  Navattic,
  SpecSchema,
  SourceRequestSchema,
  SourceResponseSchema,
  PyAirbyteExample,
  ProductInformation,
  Details,
  EntityRelationshipDiagram,
  CardWithIcon,
  Grid,
  YoutubeEmbed,
  DocMetaTags,
  CopyPageButton,
};
