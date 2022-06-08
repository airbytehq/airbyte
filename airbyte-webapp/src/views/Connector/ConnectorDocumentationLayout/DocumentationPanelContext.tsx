import { createContext, useContext, useEffect, useState } from "react";

// @ts-expect-error Default value provided at implementation
const DocumentationPanelContext = createContext<ReturnType<typeof useDocumentationPanelState>>();

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

export const useCloseDocumentationPanelEffect = () => {
  const { setDocumentationPanelOpen } = useDocumentationPanelState();
  useEffect(() => {
    return setDocumentationPanelOpen(false);
  }, [setDocumentationPanelOpen]);
};

export const useDocumentationPanelContext = () => useContext(DocumentationPanelContext);

export const DocumentationPanelProvider: React.FC = ({ children }) => {
  return (
    <DocumentationPanelContext.Provider value={useDocumentationPanelState()}>
      {children}
    </DocumentationPanelContext.Provider>
  );
};
