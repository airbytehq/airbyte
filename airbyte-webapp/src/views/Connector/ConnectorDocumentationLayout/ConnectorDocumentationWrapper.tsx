import { ConnectorDocumentationLayout } from "./ConnectorDocumentationLayout";
import { DocumentationPanelProvider } from "./DocumentationPanelContext";

export const ConnectorDocumentationWrapper: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  return (
    <DocumentationPanelProvider>
      <ConnectorDocumentationLayout>{children}</ConnectorDocumentationLayout>
    </DocumentationPanelProvider>
  );
};
