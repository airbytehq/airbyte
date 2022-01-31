import React from "react";
import sanitizeHtml from "sanitize-html";

type IProps = {
  text?: string;
};

const TextWithHTML: React.FC<IProps> = ({ text }) => {
  if (!text) {
    return null;
  }

  const sanitizedHtmlText = sanitizeHtml(text, {
    transformTags: {
      a: sanitizeHtml.simpleTransform("a", {
        target: "_blank",
        rel: "noreferrer noopener",
      }),
    },
  });

  return <span dangerouslySetInnerHTML={{ __html: sanitizedHtmlText }} />;
};

export default TextWithHTML;
