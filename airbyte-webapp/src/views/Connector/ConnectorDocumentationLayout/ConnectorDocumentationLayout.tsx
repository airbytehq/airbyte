import React, { lazy, Suspense } from "react";
import { FormattedMessage } from "react-intl";
import { useWindowSize } from "react-use";

import { LoadingPage } from "components/LoadingPage";
import { TwoPanelLayout } from "components/ui/TwoPanelLayout";

import { useDocumentationPanelContext } from "./DocumentationPanelContext";

const LazyDocumentationPanel = lazy(() =>
  import("components/DocumentationPanel").then(({ DocumentationPanel }) => ({ default: DocumentationPanel }))
);

export const ConnectorDocumentationLayout: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { documentationPanelOpen } = useDocumentationPanelContext();
  const screenWidth = useWindowSize().width;

  const documentationPanel = (
    <Suspense fallback={<LoadingPage />}>
      <LazyDocumentationPanel />
    </Suspense>
  );

  return (
    <TwoPanelLayout
      leftPanel={{ children, smallWidthHeader: <FormattedMessage id="connectorForm.expandForm" /> }}
      rightPanel={{
        children: documentationPanel,
        smallWidthHeader: <FormattedMessage id="connector.setupGuide" />,
        showPanel: screenWidth > 500 && documentationPanelOpen,
      }}
    />
  );
};
