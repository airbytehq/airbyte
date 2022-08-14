import { Root } from "mdast";
import { Plugin } from "unified";
import { Node } from "unist";
import { visit } from "unist-util-visit";

const SUPPORTED_ADMONITION_NAMES: Readonly<string[]> = ["note", "tip", "info", "caution", "warning", "danger"];
const SUPPORTED_NODE_TYPES: Readonly<string[]> = ["textDirective", "leafDirective", "containerDirective"];

export const remarkAdmonitionsPlugin: Plugin<[], Root> = () => (tree) => {
  visit<Node & { name?: string }>(tree, (node) => {
    if (!node.name || !SUPPORTED_ADMONITION_NAMES.includes(node.name) || !SUPPORTED_NODE_TYPES.includes(node.type)) {
      return;
    }

    const data = node.data ?? (node.data = {});
    const className = `admonition admonition--${node.name}`;

    data.hName = "div";
    data.hProperties = { class: className };
  });
};
