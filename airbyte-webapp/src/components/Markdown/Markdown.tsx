import type { PluggableList } from "react-markdown/lib/react-markdown";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkFrontmatter from "remark-frontmatter";
import remarkGfm from "remark-gfm";
import styled from "styled-components";

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
      className={className}
      skipHtml
      // @ts-expect-error remarkFrontmatter currently has type conflicts due to duplicate vfile dependencies
      // This is not actually causing any issues, but requires to disable TS on this for now.
      remarkPlugins={[remarkFrontmatter, remarkGfm]}
      rehypePlugins={rehypePlugins}
      children={content || ""}
    />
  );
};

const StyledMarkdown = styled(Markdown)`
  * {
    color: ${({ theme }) => theme.textColor};
    line-height: 24px;
    font-size: 16px;
    font-weight: 400;
  }

  h1 {
    font-size: 48px;
    line-height: 56px;
    font-weight: bold;
  }

  h2 {
    font-size: 24px;
    line-height: 36px;
    font-weight: bold;
  }

  h3 {
    font-size: 18px;
    font-weight: bold;
  }

  h4 {
    font-weight: bold;
  }

  a {
    color: ${({ theme }) => theme.primaryColor};
    text-decoration: none;
    line-height: 24px;

    &:hover {
      text-decoration: underline;
    }
  }

  table {
    border-collapse: collapse;
  }

  th,
  td {
    border: 1px solid ${({ theme }) => theme.borderTableColor};
    margin: 0;
    padding: 8px 16px;
  }

  th {
    background: ${({ theme }) => theme.lightTableColor};
  }

  blockquote {
    border-left: 4px solid ${({ theme }) => theme.borderTableColor};
    padding-left: 16px;
    margin-left: 25px;
  }

  strong {
    font-weight: bold;
  }

  code {
    background: ${({ theme }) => theme.lightTableColor};

    &.language-sql,
    &.language-text {
      display: block;
      padding: 15px;
      overflow: auto;
    }
  }

  img {
    max-width: 100%;
  }
`;

export default StyledMarkdown;
