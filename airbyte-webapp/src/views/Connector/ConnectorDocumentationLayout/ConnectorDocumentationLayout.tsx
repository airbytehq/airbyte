import { faGripLinesVertical } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React, { lazy, Suspense, useRef, useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";
import { useWindowSize } from "react-use";
import styled from "styled-components";

import { LoadingPage } from "components/LoadingPage";

import styles from "./ConnectorDocumentationLayout.module.scss";
import { useDocumentationPanelContext } from "./DocumentationPanelContext";

const PageContainer = styled.div<{
  offsetTop: number;
}>`
  height: calc(100% - ${({ offsetTop }) => offsetTop}px);
`;

const PnelGrabber = styled.div<{
  offsetTop: number;
}>`
  height: calc(100vh - ${({ offsetTop }) => offsetTop}px);
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const LazyDocumentationPanel = lazy(() =>
  import("components/DocumentationPanel").then(({ DocumentationPanel }) => ({ default: DocumentationPanel }))
);

interface PanelContainerProps {
  dimensions?: {
    width: number;
    height: number;
  };
}

const LeftPanelContainer: React.FC<React.PropsWithChildren<PanelContainerProps>> = ({ children, dimensions }) => {
  const width = dimensions?.width ?? 0;
  const screenWidth = useWindowSize().width;

  return (
    <div className={classNames(styles.container)}>
      {screenWidth > 500 && width < 550 && (
        <div className={styles.darkOverlay}>
          <h3>
            <FormattedMessage id="connectorForm.expandForm" />
          </h3>
        </div>
      )}
      {children}
    </div>
  );
};

const RightPanelContainer: React.FC<React.PropsWithChildren<PanelContainerProps>> = ({ children, dimensions }) => {
  const width = dimensions?.width ?? 0;

  return (
    <>
      {width < 350 ? (
        <div className={classNames(styles.rightPanelContainer, styles.lightOverlay)}>
          <h2 className={styles.rotatedHeader}>
            <FormattedMessage id="form.setupGuide" />
          </h2>
        </div>
      ) : (
        <div className={styles.rightPanelContainer}>{children}</div>
      )}
    </>
  );
};
// NOTE: ReflexElement will not load its contents if wrapped in an empty jsx tag along with ReflexSplitter.  They must be evaluated/rendered separately.

export const ConnectorDocumentationLayout: React.FC = ({ children }) => {
  const { documentationPanelOpen } = useDocumentationPanelContext();
  const screenWidth = useWindowSize().width;
  const [offsetTop, setOffsetTop] = useState<number>(70);

  const divRef = useRef(null);
  useEffect(() => {
    const top: number = divRef.current ? divRef.current?.["offsetTop"] : 0;
    setOffsetTop(top);
  }, [documentationPanelOpen]);

  return (
    <PageContainer ref={divRef} offsetTop={offsetTop}>
      <ReflexContainer orientation="vertical">
        <ReflexElement className={styles.leftPanelStyle} propagateDimensions minSize={150}>
          <LeftPanelContainer>{children}</LeftPanelContainer>
        </ReflexElement>
        {documentationPanelOpen && (
          <ReflexSplitter style={{ border: 0, background: "rgba(255, 165, 0, 0)", display: "flex" }}>
            <PnelGrabber offsetTop={offsetTop}>
              <FontAwesomeIcon className={styles.grabberHandleIcon} icon={faGripLinesVertical} size="1x" />
            </PnelGrabber>
          </ReflexSplitter>
        )}
        {screenWidth > 500 && documentationPanelOpen && (
          <ReflexElement className={styles.rightPanelStyle} size={1000} propagateDimensions minSize={60}>
            <RightPanelContainer>
              <Suspense fallback={<LoadingPage />}>
                <LazyDocumentationPanel />
              </Suspense>
            </RightPanelContainer>
          </ReflexElement>
        )}
      </ReflexContainer>
    </PageContainer>
  );
};
