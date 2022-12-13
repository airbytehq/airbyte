import classNames from "classnames";
import React from "react";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";

import { Heading } from "components/ui/Heading";

import styles from "./ResizablePanels.module.scss";

interface ResizablePanelsProps {
  className?: string;
  orientation?: "vertical" | "horizontal";
  firstPanel: PanelProps;
  secondPanel: PanelProps;
  hideSecondPanel?: boolean;
}

interface PanelProps {
  children: React.ReactNode;
  minWidth: number;
  className?: string;
  flex?: number;
  overlay?: Overlay;
  onStopResize?: (newFlex: number | undefined) => void;
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
  orientation = "vertical",
  firstPanel,
  secondPanel,
  hideSecondPanel = false,
}) => {
  return (
    <ReflexContainer className={className} orientation={orientation}>
      <ReflexElement
        className={classNames(styles.panelStyle, firstPanel.className)}
        propagateDimensions
        minSize={firstPanel.minWidth}
        flex={firstPanel.flex}
        onStopResize={(args) => {
          firstPanel.onStopResize?.(args.component.props.flex);
        }}
      >
        <PanelContainer overlay={firstPanel.overlay}>{firstPanel.children}</PanelContainer>
      </ReflexElement>
      {/* NOTE: ReflexElement will not load its contents if wrapped in an empty jsx tag along with ReflexSplitter.  They must be evaluated/rendered separately. */}
      {!hideSecondPanel && (
        <ReflexSplitter className={styles.splitter}>
          <div
            className={classNames({
              [styles.panelGrabberVertical]: orientation === "vertical",
              [styles.panelGrabberHorizontal]: orientation === "horizontal",
            })}
          >
            <div
              className={classNames(styles.handleIcon, {
                [styles.handleIconVertical]: orientation === "vertical",
                [styles.handleIconHorizontal]: orientation === "horizontal",
              })}
            />
          </div>
        </ReflexSplitter>
      )}
      {!hideSecondPanel && (
        <ReflexElement
          className={classNames(styles.panelStyle, secondPanel.className)}
          propagateDimensions
          minSize={secondPanel.minWidth}
          flex={secondPanel.flex}
          onStopResize={(args) => {
            secondPanel.onStopResize?.(args.component.props.flex);
          }}
        >
          <PanelContainer overlay={secondPanel.overlay}>{secondPanel.children}</PanelContainer>
        </ReflexElement>
      )}
    </ReflexContainer>
  );
};
