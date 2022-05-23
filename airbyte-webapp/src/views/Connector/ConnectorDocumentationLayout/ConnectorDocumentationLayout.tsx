import { faGripLinesVertical } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";
import styled from "styled-components";

import { DocumentationPanel } from "../../../components/DocumentationPanel/DocumentationPanel";
import styles from "./ConnectorDocumentationLayout.module.css";
import { useDocumentationPanelContext } from "./DocumentationPanelContext";

const PanelGrabber = styled.div`
  height: 100vh;
  padding: 6px;
  display: flex;
`;

const GrabberHandle = styled(FontAwesomeIcon)`
  margin: auto;
  height: 25px;
  color: ${({ theme }) => theme.greyColor20};
`;

interface PanelContainerProps {
  dimensions?: {
    width: number;
    height: number;
  };
}

const LeftPanelContainer: React.FC<React.PropsWithChildren<PanelContainerProps>> = ({ children, dimensions }) => {
  const width = dimensions?.width ?? 0;
  return (
    <>
      {width < 450 && (
        <div className={styles.darkOverlay}>
          <h3>
            <FormattedMessage id="connectorForm.expandForm" />
          </h3>
        </div>
      )}
      <div className={width < 550 ? `${styles.noScroll}` : `${styles.fullHeight}`}>{children}</div>{" "}
    </>
  );
};

const RightPanelContainer: React.FC<React.PropsWithChildren<PanelContainerProps>> = ({ children, dimensions }) => {
  const width = dimensions?.width ?? 0;

  return (
    <>
      {width < 350 ? (
        <div className={`${styles.lightOverlay}`}>
          <h2 className={styles.rotatedHeader}>Setup Guide</h2>
        </div>
      ) : (
        <div>{children}</div>
      )}
    </>
  );
};
//NOTE: ReflexElement will not load its contents if wrapped in an empty jsx tag along with ReflexSplitter.  They must be evaluated/rendered separately.

export const ConnectorDocumentationLayout: React.FC = ({ children }) => {
  const { documentationPanelOpen } = useDocumentationPanelContext();

  return (
    <ReflexContainer orientation="vertical" windowResizeAware>
      <ReflexElement className={`left-pane ${styles.leftPanelClass}`} propagateDimensions minSize={150}>
        <LeftPanelContainer>{children}</LeftPanelContainer>
      </ReflexElement>
      {documentationPanelOpen && (
        <ReflexSplitter style={{ border: 0, background: "rgba(255, 165, 0, 0)" }}>
          <PanelGrabber>
            <GrabberHandle icon={faGripLinesVertical} size={"1x"} />
          </PanelGrabber>
        </ReflexSplitter>
      )}
      {documentationPanelOpen && (
        <ReflexElement className="right-pane" size={1000} propagateDimensions minSize={60}>
          <RightPanelContainer>
            <DocumentationPanel />
          </RightPanelContainer>
        </ReflexElement>
      )}
    </ReflexContainer>
  );
};
