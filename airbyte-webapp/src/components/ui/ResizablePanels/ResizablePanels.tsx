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

// export const ResizablePanels: React.FC<React.PropsWithChildren<ResizablePanelsProps>> & {
//   Panel: React.FC<PropsWithChildren<PanelProps>>;
//   Splitter: React.FC;
// } = ({ children, className }) => {
//   return (
//     <ReflexContainer className={className} orientation="vertical">
//       {children}
//     </ReflexContainer>
//   );
// };

export class ResizablePanels extends React.Component<React.PropsWithChildren<ResizablePanelsProps>> {
  render() {
    const { children, className } = this.props;

    return (
      <ReflexContainer className={className} orientation="vertical">
        {children}
      </ReflexContainer>
    );
  }
}

interface Overlay {
  displayThreshold: number;
  header: string;
  rotation: "clockwise" | "counter-clockwise";
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
          <Text as="h2" className={styles.rotatedHeader}>
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
  startingFlex?: number;
  minWidth?: number;
  overlay?: Overlay;
}

// export const Panel: React.FC<PropsWithChildren<PanelProps>> = ({
//   children,
//   className,
//   startingFlex,
//   minWidth,
//   overlay,
// }) => {
// return (
//   <ReflexElement className={styles.panelStyle} propagateDimensions minSize={minWidth} flex={startingFlex}>
//     <PanelContainer className={className} overlay={overlay}>
//       {children}
//     </PanelContainer>
//   </ReflexElement>
// );
// };

export class Panel extends React.Component<React.PropsWithChildren<PanelProps>> {
  render() {
    const { children, className, startingFlex, minWidth, overlay } = this.props;

    return (
      <ReflexElement className={styles.panelStyle} propagateDimensions minSize={minWidth} flex={startingFlex}>
        <PanelContainer className={className} overlay={overlay}>
          {children}
        </PanelContainer>
      </ReflexElement>
    );
  }
}

// export const Splitter: React.FC<unknown> = () => (
//   <ReflexSplitter className={styles.splitter}>
//     <div className={styles.panelGrabber}>
//       <FontAwesomeIcon className={styles.grabberHandleIcon} icon={faGripLinesVertical} size="1x" />
//     </div>
//   </ReflexSplitter>
// );

export class Splitter extends React.Component {
  render() {
    return (
      <ReflexSplitter className={styles.splitter}>
        <div className={styles.panelGrabber}>
          <FontAwesomeIcon className={styles.grabberHandleIcon} icon={faGripLinesVertical} size="1x" />
        </div>
      </ReflexSplitter>
    );
  }
}
