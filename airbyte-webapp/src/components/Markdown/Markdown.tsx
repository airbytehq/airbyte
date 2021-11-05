import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import styled from "styled-components";

const Container = styled.div`
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

type Props = {
  content?: string;
};

const Markdown: React.FC<Props> = ({ content }) => {
  return (
    <Container>
      <ReactMarkdown
        linkTarget="_blank"
        remarkPlugins={[remarkGfm]}
        children={content || ""}
      />
    </Container>
  );
};

export default Markdown;
