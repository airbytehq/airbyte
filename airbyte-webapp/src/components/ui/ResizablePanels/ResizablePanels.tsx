import { faGripLinesVertical } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";
import { useWindowSize } from "react-use";

import styles from "./ResizablePanels.module.scss";

interface ResizablePanelsProps {
  leftPanel: {
    children: React.ReactNode;
    smallWidthHeader: React.ReactNode;
    className?: string;
  };
  rightPanel: {
    children: React.ReactNode;
    smallWidthHeader: React.ReactNode;
    showPanel: boolean;
    className?: string;
  };
  containerClassName?: string;
}

interface PanelContainerProps {
  smallWidthHeader: React.ReactNode;
  dimensions?: {
    width: number;
    height: number;
  };
  className?: string;
}

const LeftPanelContainer: React.FC<React.PropsWithChildren<PanelContainerProps>> = ({
  children,
  dimensions,
  smallWidthHeader,
  className,
}) => {
  const width = dimensions?.width ?? 0;
  const screenWidth = useWindowSize().width;

  return (
    <div className={classNames(className, styles.leftPanelContainer)}>
      {screenWidth > 500 && width < 550 && (
        <div className={styles.darkOverlay}>
          <h3>{smallWidthHeader}</h3>
        </div>
      )}
      {children}
    </div>
  );
};

const RightPanelContainer: React.FC<React.PropsWithChildren<PanelContainerProps>> = ({
  children,
  dimensions,
  smallWidthHeader,
  className,
}) => {
  const width = dimensions?.width ?? 0;

  return (
    <>
      {width < 350 ? (
        <div className={classNames(className, styles.rightPanelContainer, styles.lightOverlay)}>
          <h2 className={styles.rotatedHeader}>{smallWidthHeader}</h2>
        </div>
      ) : (
        <div className={classNames(className, styles.rightPanelContainer)}>{children}</div>
      )}
    </>
  );
};
// NOTE: ReflexElement will not load its contents if wrapped in an empty jsx tag along with ReflexSplitter.  They must be evaluated/rendered separately.

export const ResizablePanels: React.FC<ResizablePanelsProps> = ({ leftPanel, rightPanel, containerClassName }) => {
  return (
    <ReflexContainer className={containerClassName} orientation="vertical">
      <ReflexElement className={styles.leftPanelStyle} propagateDimensions minSize={150}>
        <LeftPanelContainer className={leftPanel.className} smallWidthHeader={leftPanel.smallWidthHeader}>
          {leftPanel.children}
        </LeftPanelContainer>
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
          <RightPanelContainer className={rightPanel.className} smallWidthHeader={rightPanel.smallWidthHeader}>
            {rightPanel.children}
          </RightPanelContainer>
        </ReflexElement>
      )}
    </ReflexContainer>
  );
};
