import { faGripLinesVertical } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";

import { Text } from "../Text";
import styles from "./ResizablePanels.module.scss";

interface ResizablePanelsProps {
  className?: string;
}

// NOTE: ReflexElement will not load its contents if wrapped in an empty jsx tag along with ReflexSplitter.  They must be evaluated/rendered separately.

export const ResizablePanels: React.FC<React.PropsWithChildren<ResizablePanelsProps>> = ({ children, className }) => {
  return (
    <ReflexContainer className={className} orientation="vertical">
      {children}
    </ReflexContainer>
  );
};

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
          <Text
            as="h2"
            className={classNames(styles.rotatedHeader, {
              [styles.counterClockwise]: overlay?.rotation === "counter-clockwise",
            })}
          >
            {overlay.header}
          </Text>
        </div>
      )}
      {children}
    </div>
  );
};
interface PanelProps {
  className?: string;
  flex?: number;
  minWidth?: number;
  overlay?: Overlay;
}

export const Panel = React.forwardRef<ReflexElement, React.PropsWithChildren<PanelProps>>(
  ({ children, className, minWidth, overlay, ...rest }, ref) => {
    return (
      <ReflexElement
        flex={0.5}
        className={styles.panelStyle}
        propagateDimensions
        minSize={minWidth}
        ref={ref}
        {...rest}
      >
        <PanelContainer className={className} overlay={overlay}>
          {children}
        </PanelContainer>
      </ReflexElement>
    );
  }
);

export const Splitter = React.forwardRef<ReflexSplitter>((props, ref) => (
  <ReflexSplitter className={styles.splitter} ref={ref} {...props}>
    <div className={styles.panelGrabber}>
      <FontAwesomeIcon className={styles.grabberHandleIcon} icon={faGripLinesVertical} size="1x" />
    </div>
  </ReflexSplitter>
));
