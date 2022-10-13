import React from "react";
import sanitizeHtml from "sanitize-html";

interface TextWithHTMLProps {
  text?: string;
  className?: string;
}

const allowedAttributes = {
  ...sanitizeHtml.defaults.allowedAttributes,
  a: [...sanitizeHtml.defaults.allowedAttributes.a, "rel"],
};

export const TextWithHTML: React.FC<TextWithHTMLProps> = ({ text, className }) => {
  if (!text) {
    return null;
  }

  const sanitizedHtmlText = sanitizeHtml(text, {
    allowedAttributes,
    transformTags: {
      a: sanitizeHtml.simpleTransform("a", {
        target: "_blank",
        rel: "noopener noreferrer",
      }),
    },
  });

  return <span className={className} dangerouslySetInnerHTML={{ __html: sanitizedHtmlText }} />;
};
