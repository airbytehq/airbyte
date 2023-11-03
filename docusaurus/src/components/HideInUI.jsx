import React from "react";

/**
 * HideInUI is a dummy-component in the docusaurus build but is used when the documentation is rendered in the webapp
 * to suppress rendering of certain content.
 *
 * When using the HideInUI component, you must leave a blank line between the tags and its
 * content in order for the content to be parsed as markdown and rendered to html; without
 * a blank line, it will be rendered as plain text.
 */
export const HideInUI = ({ children }) => {
  return children;
};
