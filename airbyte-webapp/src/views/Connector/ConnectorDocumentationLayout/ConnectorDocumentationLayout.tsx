import React, { lazy, Suspense } from "react";
import { useIntl } from "react-intl";
import { useWindowSize } from "react-use";

import { LoadingPage } from "components/LoadingPage";
import { Panel, ResizablePanels, Splitter } from "components/ui/ResizablePanels";

import styles from "./ConnectorDocumentationLayout.module.scss";
import { useDocumentationPanelContext } from "./DocumentationPanelContext";

const LazyDocumentationPanel = lazy(() =>
  import("components/DocumentationPanel").then(({ DocumentationPanel }) => ({ default: DocumentationPanel }))
);

export const ConnectorDocumentationLayout: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { formatMessage } = useIntl();
  const { documentationPanelOpen } = useDocumentationPanelContext();
  const screenWidth = useWindowSize().width;
  const showDocumentationPanel = screenWidth > 500 && documentationPanelOpen;

  return (
    <ResizablePanels>
      <Panel className={styles.leftPanel} minWidth={500}>
        {children}
      </Panel>
      {/* // NOTE: ReflexElement will not load its contents if wrapped in an empty jsx tag along with ReflexSplitter.  They must be evaluated/rendered separately. */}
      {showDocumentationPanel && <Splitter />}
      {showDocumentationPanel && (
        <Panel
          minWidth={60}
          overlay={{
            displayThreshold: 350,
            header: formatMessage({ id: "connector.setupGuide" }),
            rotation: "counter-clockwise",
          }}
        >
          <Suspense fallback={<LoadingPage />}>
            <LazyDocumentationPanel />
          </Suspense>
        </Panel>
      )}
    </ResizablePanels>
  );
};
