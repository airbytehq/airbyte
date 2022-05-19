import { ConnectorDocumentationLayout } from "./ConnectorDocumentationLayout";
import { DocumentationPanelProvider } from "./DocumentationPanelContext";

export const ConnectorDocumentationWrapper: React.FC = ({ children }) => {
  return (
    <DocumentationPanelProvider>
      <ConnectorDocumentationLayout>{children}</ConnectorDocumentationLayout>
    </DocumentationPanelProvider>
  );
};
