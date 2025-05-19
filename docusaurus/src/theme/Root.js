import MarkpromptChat from "@site/src/components/MarkpromptChat/MarkpromptChat";
import React from "react";

export default function Root({ children }) {
  return (
    <>
      {children}
      <MarkpromptChat />
    </>
  );
}
