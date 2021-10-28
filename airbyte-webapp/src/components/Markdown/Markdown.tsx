import React from "react";
import ReactMarkdown from "react-markdown";
import remark from "remark-gfm";

type Props = {
  content?: string;
};

const Markdown: React.FC<Props> = ({ content }) => {
  return <ReactMarkdown remarkPlugins={[remark]} children={content || ""} />;
};

export default Markdown;
