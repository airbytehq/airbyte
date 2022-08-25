import { createContext, useCallback, useContext, useState } from "react";

export type DocumentationPanelContext = ReturnType<typeof useDocumentationPanelState>;

export const useDocumentationPanelState = () => {
  const [documentationPanelOpen, setDocumentationPanelOpen] = useState(false);
  const [documentationUrl, setDocumentationUrlState] = useState("");

  /* Ad blockers prevent the Google Ads docs .md file from rendering.  Because these URLs are
   * standardized, we work around this without changing the main file URL by:
   *   1. Changing the name of the .md in the Gradle build
   *       a. the docs we render aren't actually fetching from our website, they're compiled with our build
   *       b. when running on localhost, we fetch them with our proxy, so there is an additional piece in setupProxy.js for that case
   *   2. Changing the URL here to match the renamed .md file
   */

  const setDocumentationUrl = useCallback((url: string) => {
    setDocumentationUrlState(url.replace("google-ads", "gglad"));
  }, []);

  return {
    documentationPanelOpen,
    setDocumentationPanelOpen,
    documentationUrl,
    setDocumentationUrl,
  };
};

// @ts-expect-error Default value provided at implementation
export const documentationPanelContext = createContext<DocumentationPanelContext>();

export const useDocumentationPanelContext = () => useContext(documentationPanelContext);

export const DocumentationPanelProvider: React.FC = ({ children }) => {
  return (
    <documentationPanelContext.Provider value={useDocumentationPanelState()}>
      {children}
    </documentationPanelContext.Provider>
  );
};
