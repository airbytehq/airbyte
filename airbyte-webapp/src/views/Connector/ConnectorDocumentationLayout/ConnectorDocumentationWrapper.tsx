import { DocumentationPanelProvider } from "./ConnectorDocumentationContext";
import { ConnectorDocumentationLayout } from "./ConnectorDocumentationLayout";

export const ConnectorDocumentationWrapper: React.FC = ({ children }) => {
  return (
    <DocumentationPanelProvider>
      <ConnectorDocumentationLayout>{children}</ConnectorDocumentationLayout>
    </DocumentationPanelProvider>
  );
};
