import { DocumentationPanelProvider } from "./ConnectorDocumentationContext";
import { ConnectorDocumentationLayout } from "./ConnectorDocumentationLayout";

export const ConnectorDocumentationWrapper = ({ children }: { children: React.ReactNode | React.ReactNode[] }) => {
  return (
    <DocumentationPanelProvider>
      <ConnectorDocumentationLayout>{children}</ConnectorDocumentationLayout>
    </DocumentationPanelProvider>
  );
};
