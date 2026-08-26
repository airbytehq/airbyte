import React from "react";
import styles from "./ApiReference.module.css";

/**
 * Semantic wrappers emitted by the pdoc3 markdown template
 * (docusaurus/pdoc-templates/text.mako) around auto-generated API reference
 * content. They own the visual presentation of API members so the generator
 * stays presentation-agnostic.
 */

export const ApiSignature = ({ children }) => (
  <div className={styles.apiSignature}>{children}</div>
);

export const ApiMember = ({ kind, children }) => (
  <div className={styles.apiMember} data-kind={kind}>
    {kind && <span className={styles.kindBadge}>{kind}</span>}
    {children}
  </div>
);
