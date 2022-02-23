import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import styled from "styled-components";

type Props = {
  content?: string;
  className?: string;
};

const Markdown: React.FC<Props> = ({ content, className }) => {
  return (
    <ReactMarkdown
      linkTarget="_blank"
      className={className}
      remarkPlugins={[remarkGfm]}
      children={content || ""}
    />
  );
};

const StyledMarkdown = styled(Markdown)`
  * {
    color: rgba(59, 69, 78, 1);
    line-height: 20px;
    font-weight: 400;
  }

  h1 {
    font-size: 48px;
    line-height: 56px;
  }

  a {
    color: rgb(26, 25, 117);
    text-decoration: none;
    line-height: 24px;

    &:hover {
      text-decoration: underline;
    }
  }
`;

export default StyledMarkdown;
