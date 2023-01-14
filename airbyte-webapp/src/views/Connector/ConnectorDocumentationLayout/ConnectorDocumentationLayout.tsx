import React, { lazy, Suspense } from "react";
import { useIntl } from "react-intl";
import { useWindowSize } from "react-use";

import { LoadingPage } from "components/LoadingPage";
import { ResizablePanels } from "components/ui/ResizablePanels";

import styles from "./ConnectorDocumentationLayout.module.scss";
import { useDocumentationPanelContext } from "./DocumentationPanelContext";

const LazyDocumentationPanel = lazy(() =>
  import("./DocumentationPanel").then(({ DocumentationPanel }) => ({ default: DocumentationPanel }))
);

export const ConnectorDocumentationLayout: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { formatMessage } = useIntl();
  const { documentationPanelOpen } = useDocumentationPanelContext();
  const screenWidth = useWindowSize().width;
  const showDocumentationPanel = screenWidth > 500 && documentationPanelOpen;

  const documentationPanel = (
    <Suspense fallback={<LoadingPage />}>
      <LazyDocumentationPanel />
    </Suspense>
  );

  return (
    <ResizablePanels
      hideSecondPanel={!showDocumentationPanel}
      firstPanel={{
        children,
        className: styles.leftPanel,
        minWidth: 500,
      }}
      secondPanel={{
        children: documentationPanel,
        minWidth: 60,
        overlay: {
          displayThreshold: 350,
          header: formatMessage({ id: "connector.setupGuide" }),
          rotation: "counter-clockwise",
        },
      }}
    />
  );
};
