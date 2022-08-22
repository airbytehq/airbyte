import type { PluggableList } from "react-markdown/lib/react-markdown";

import classNames from "classnames";
import React from "react";
import ReactMarkdown from "react-markdown";
import remarkDirective from "remark-directive";
import remarkFrontmatter from "remark-frontmatter";
import remarkGfm from "remark-gfm";

import styles from "./Markdown.module.scss";
import { remarkAdmonitionsPlugin } from "./remarkAdmonitionsPlugin";

interface MarkdownProps {
  content?: string;
  className?: string;
  rehypePlugins?: PluggableList;
}

export const Markdown: React.VFC<MarkdownProps> = ({ content, className, rehypePlugins }) => {
  return (
    <ReactMarkdown
      // Open everything except fragment only links in a new tab
      linkTarget={(href) => (href.startsWith("#") ? undefined : "_blank")}
      className={classNames(styles.markdown, className)}
      skipHtml
      // @ts-expect-error remarkFrontmatter currently has type conflicts due to duplicate vfile dependencies
      // This is not actually causing any issues, but requires to disable TS on this for now.
      remarkPlugins={[remarkDirective, remarkAdmonitionsPlugin, remarkFrontmatter, remarkGfm]}
      rehypePlugins={rehypePlugins}
      children={content || ""}
    />
  );
};
