import { DocumentationPanelProvider } from "./ConnectorDocumentationContext";
import { ConnectorDocumentationLayout } from "./ConnectorDocumentationLayout";

export const ConnectorDocumentationWrapper = ({ children }: { children: JSX.Element }) => {
  return (
    <DocumentationPanelProvider>
      <ConnectorDocumentationLayout>{children}</ConnectorDocumentationLayout>
    </DocumentationPanelProvider>
  );
};
