import { faGripLinesVertical } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";

import { Heading } from "components/ui/Heading";

import styles from "./ResizablePanels.module.scss";

interface ResizablePanelsProps {
  className?: string;
  hideRightPanel?: boolean;
  leftPanel: PanelProps;
  rightPanel: PanelProps;
}

interface PanelProps {
  children: React.ReactNode;
  minWidth: number;
  className?: string;
  startingFlex?: number;
  overlay?: Overlay;
}

interface Overlay {
  displayThreshold: number;
  header: string;
  rotation?: "clockwise" | "counter-clockwise";
}

interface PanelContainerProps {
  className?: string;
  dimensions?: {
    width: number;
    height: number;
  };
  overlay?: Overlay;
}

const PanelContainer: React.FC<React.PropsWithChildren<PanelContainerProps>> = ({
  children,
  className,
  dimensions,
  overlay,
}) => {
  const width = dimensions?.width ?? 0;

  return (
    <div className={classNames(className, styles.panelContainer)}>
      {overlay && width <= overlay.displayThreshold && (
        <div className={styles.lightOverlay}>
          <Heading
            as="h2"
            className={classNames(styles.rotatedHeader, {
              [styles.counterClockwise]: overlay?.rotation === "counter-clockwise",
            })}
          >
            {overlay.header}
          </Heading>
        </div>
      )}
      {children}
    </div>
  );
};

export const ResizablePanels: React.FC<ResizablePanelsProps> = ({
  className,
  hideRightPanel = false,
  leftPanel,
  rightPanel,
}) => {
  return (
    <ReflexContainer className={className} orientation="vertical">
      <ReflexElement
        className={styles.panelStyle}
        propagateDimensions
        minSize={leftPanel.minWidth}
        flex={leftPanel.startingFlex}
      >
        <PanelContainer className={leftPanel.className} overlay={leftPanel.overlay}>
          {leftPanel.children}
        </PanelContainer>
      </ReflexElement>
      {/* NOTE: ReflexElement will not load its contents if wrapped in an empty jsx tag along with ReflexSplitter.  They must be evaluated/rendered separately. */}
      {!hideRightPanel && (
        <ReflexSplitter className={styles.splitter}>
          <div className={styles.panelGrabber}>
            <FontAwesomeIcon className={styles.grabberHandleIcon} icon={faGripLinesVertical} size="1x" />
          </div>
        </ReflexSplitter>
      )}
      {!hideRightPanel && (
        <ReflexElement
          className={styles.panelStyle}
          propagateDimensions
          minSize={rightPanel.minWidth}
          flex={rightPanel.startingFlex}
        >
          <PanelContainer className={rightPanel.className} overlay={rightPanel.overlay}>
            {rightPanel.children}
          </PanelContainer>
        </ReflexElement>
      )}
    </ReflexContainer>
  );
};
