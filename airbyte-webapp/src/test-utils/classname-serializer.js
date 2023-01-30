import { prettyDOM } from "@testing-library/react";

/**
 * Traverse a tree of nodes and replace all class names with "<removed-for-snapshot-test>"
 */
const traverseAndRedactClasses = (node) => {
  if (
    node.className &&
    (typeof node.className === "string" || (node.className instanceof SVGAnimatedString && node.className.baseVal))
  ) {
    // We need to use setAttribute here, since on SVGElement we can't
    // set `className` to a string for the `SVGAnimatedString` case.
    node.setAttribute("class", `<removed-for-snapshot-test>`);
  }
  node.childNodes.forEach(traverseAndRedactClasses);
};

module.exports = {
  serialize(val, config) {
    // Clone the whole rendered DOM tree, since we're modifying it
    const clone = val.baseElement.cloneNode(true);
    // Redact all classnames
    traverseAndRedactClasses(clone);
    // Use prettyDOM to format the modified DOM as a string.
    return prettyDOM(clone, Infinity, {
      indent: config.indent.length,
      highlight: false,
    });
  },

  test(val) {
    // Only use this serializer when creating a snapshot of RenderResult, which is
    // the return value of testing-library/react's render method.
    return val && val.baseElement && val.baseElement instanceof Element;
  },
};
