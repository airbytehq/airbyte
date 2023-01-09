import { Root } from "mdast";
import { Plugin } from "unified";
import { Node } from "unist";
import { visit } from "unist-util-visit";

// Since we're dynamically accessing the admonition--{node.name} classes, the linter
// can't determine that those are used, thus we need to ignore unused classes here.
// eslint-disable-next-line css-modules/no-unused-class
import styles from "./admonitions.module.scss";

const SUPPORTED_ADMONITION_NAMES: Readonly<string[]> = ["note", "tip", "info", "caution", "warning", "danger"];
const SUPPORTED_NODE_TYPES: Readonly<string[]> = ["textDirective", "leafDirective", "containerDirective"];

export const remarkAdmonitionsPlugin: Plugin<[], Root> = () => (tree) => {
  visit<Node & { name?: string }>(tree, (node) => {
    if (!node.name || !SUPPORTED_ADMONITION_NAMES.includes(node.name) || !SUPPORTED_NODE_TYPES.includes(node.type)) {
      return;
    }

    const data = node.data ?? (node.data = {});
    const className = `${styles.admonition} ${styles[`admonition--${node.name}`]}`;

    data.hName = "div";
    data.hProperties = { class: className };
  });
};
