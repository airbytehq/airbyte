import { createContext, useContext, useState } from "react";

// @ts-expect-error Default value provided at implementation
export const DocumenationPanelContext = createContext<ReturnType<typeof useDocumentationPanelState>>();

export const useDocumentationPanelState = () => {
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
  return (
    <DocumenationPanelContext.Provider value={useDocumentationPanelState()}>
      {children}
    </DocumenationPanelContext.Provider>
  );
};
