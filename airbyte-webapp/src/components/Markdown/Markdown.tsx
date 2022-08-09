import type { PluggableList } from "react-markdown/lib/react-markdown";

import classNames from "classnames";
import React from "react";
import ReactMarkdown from "react-markdown";
import remarkFrontmatter from "remark-frontmatter";
import remarkGfm from "remark-gfm";

// eslint-disable-next-line css-modules/no-unused-class
import styles from "./Markdown.module.scss";

interface Props {
  content?: string;
  className?: string;
  rehypePlugins?: PluggableList;
}

const Markdown: React.FC<Props> = ({ content, className, rehypePlugins }) => {
  return (
    <ReactMarkdown
      // Open everything except fragment only links in a new tab
      linkTarget={(href) => (href.startsWith("#") ? undefined : "_blank")}
      className={classNames(styles.markdown, className)}
      skipHtml
      // @ts-expect-error remarkFrontmatter currently has type conflicts due to duplicate vfile dependencies
      // This is not actually causing any issues, but requires to disable TS on this for now.
      remarkPlugins={[remarkFrontmatter, remarkGfm]}
      rehypePlugins={rehypePlugins}
      children={content || ""}
    />
  );
};

export default Markdown;
