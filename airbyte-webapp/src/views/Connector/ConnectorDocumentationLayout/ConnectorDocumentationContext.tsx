import { createContext, useContext, useState } from "react";

// @ts-expect-error Default value provided at implementation
const DocumenationPanelContext = createContext<ReturnType<typeof useSidePanelState>>();

export const useSidePanelState = () => {
  const [documentationPanelOpen, setDocumentationPanelOpen] = useState(false);
  const [documentationUrl, setDocumentationUrl] = useState("");

  return {
    documentationPanelOpen,
    setDocumentationPanelOpen,
    documentationUrl,
    setDocumentationUrl,
  };
};

export const useDocumentationPanelContext = () => useContext(DocumenationPanelContext);

export const DocumentationPanelProvider: React.FC = ({ children }) => {
  return <DocumenationPanelContext.Provider value={useSidePanelState()}>{children}</DocumenationPanelContext.Provider>;
};
