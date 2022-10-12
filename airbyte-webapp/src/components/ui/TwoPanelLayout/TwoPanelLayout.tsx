import { faGripLinesVertical } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";
import { useWindowSize } from "react-use";

import styles from "./TwoPanelLayout.module.scss";

interface TwoPanelContainerProps {
  leftPanel: {
    children: React.ReactNode;
    smallWidthHeader: React.ReactNode;
  };
  rightPanel: {
    children: React.ReactNode;
    smallWidthHeader: React.ReactNode;
    showPanel: boolean;
  };
}

interface PanelContainerProps {
  smallWidthHeader: React.ReactNode;
  dimensions?: {
    width: number;
    height: number;
  };
}

const LeftPanelContainer: React.FC<React.PropsWithChildren<PanelContainerProps>> = ({
  children,
  dimensions,
  smallWidthHeader,
}) => {
  const width = dimensions?.width ?? 0;
  const screenWidth = useWindowSize().width;

  return (
    <div className={classNames(styles.leftPanelContainer)}>
      {screenWidth > 500 && width < 550 && (
        <div className={styles.darkOverlay}>
          <h3>{smallWidthHeader}</h3>
        </div>
      )}
      <div>{children}</div>
    </div>
  );
};

const RightPanelContainer: React.FC<React.PropsWithChildren<PanelContainerProps>> = ({
  children,
  dimensions,
  smallWidthHeader,
}) => {
  const width = dimensions?.width ?? 0;

  return (
    <>
      {width < 350 ? (
        <div className={classNames(styles.rightPanelContainer, styles.lightOverlay)}>
          <h2 className={styles.rotatedHeader}>{smallWidthHeader}</h2>
        </div>
      ) : (
        <div className={styles.rightPanelContainer}>{children}</div>
      )}
    </>
  );
};
// NOTE: ReflexElement will not load its contents if wrapped in an empty jsx tag along with ReflexSplitter.  They must be evaluated/rendered separately.

export const TwoPanelLayout: React.FC<TwoPanelContainerProps> = ({ leftPanel, rightPanel }) => {
  return (
    <ReflexContainer orientation="vertical">
      <ReflexElement className={styles.leftPanelStyle} propagateDimensions minSize={150}>
        <LeftPanelContainer smallWidthHeader={leftPanel.smallWidthHeader}>{leftPanel.children}</LeftPanelContainer>
      </ReflexElement>
      {rightPanel.showPanel && (
        <ReflexSplitter style={{ border: 0, background: "rgba(255, 165, 0, 0)" }}>
          <div className={styles.panelGrabber}>
            <FontAwesomeIcon className={styles.grabberHandleIcon} icon={faGripLinesVertical} size="1x" />
          </div>
        </ReflexSplitter>
      )}
      {rightPanel.showPanel && (
        <ReflexElement className={styles.rightPanelStyle} size={1000} propagateDimensions minSize={60}>
          <RightPanelContainer smallWidthHeader={rightPanel.smallWidthHeader}>
            {rightPanel.children}
          </RightPanelContainer>
        </ReflexElement>
      )}
    </ReflexContainer>
  );
};
