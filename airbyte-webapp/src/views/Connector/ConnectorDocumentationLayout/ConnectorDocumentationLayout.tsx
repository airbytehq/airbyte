import React, { lazy, Suspense } from "react";
import { useWindowSize } from "react-use";

import { LoadingPage } from "components/LoadingPage";
import { ResizablePanels } from "components/ui/ResizablePanels";
import { Panel, Splitter } from "components/ui/ResizablePanels/ResizablePanels";

import styles from "./ConnectorDocumentationLayout.module.scss";
import { useDocumentationPanelContext } from "./DocumentationPanelContext";

const LazyDocumentationPanel = lazy(() =>
  import("components/DocumentationPanel").then(({ DocumentationPanel }) => ({ default: DocumentationPanel }))
);

export const ConnectorDocumentationLayout: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { documentationPanelOpen } = useDocumentationPanelContext();
  const screenWidth = useWindowSize().width;
  const showDocumentationPanel = screenWidth > 500 && documentationPanelOpen;
  console.log(showDocumentationPanel);

  return (
    <ResizablePanels>
      <Panel className={styles.leftPanel} minWidth={300} flex={0.5}>
        {children}
      </Panel>
      {showDocumentationPanel && <Splitter />}
      {showDocumentationPanel && (
        <Panel flex={0.5}>
          <Suspense fallback={<LoadingPage />}>
            <LazyDocumentationPanel />
          </Suspense>
        </Panel>
      )}
    </ResizablePanels>

    // <ResizablePanels
    //   leftPanel={{
    //     children,
    //     smallWidthHeader: <FormattedMessage id="connectorForm.expandForm" />,
    //     className: styles.leftPanel,
    //   }}
    //   rightPanel={{
    //     children: documentationPanel,
    //     smallWidthHeader: <FormattedMessage id="connector.setupGuide" />,
    //     showPanel: screenWidth > 500 && documentationPanelOpen,
    //   }}
    // />
  );
};
