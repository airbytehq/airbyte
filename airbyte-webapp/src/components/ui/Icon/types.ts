import React from "react";

import { ReactComponent as ArrowRightIcon } from "./icons/arrowRightIcon.svg";
import { ReactComponent as CreditsIcon } from "./icons/creditsIcon.svg";
import { ReactComponent as CrossIcon } from "./icons/crossIcon.svg";
import { ReactComponent as DocsIcon } from "./icons/docsIcon.svg";
import { ReactComponent as GAIcon } from "./icons/gAIcon.svg";
import { ReactComponent as InfoIcon } from "./icons/infoIcon.svg";
import { ReactComponent as MinusIcon } from "./icons/minusIcon.svg";
import { ReactComponent as ModificationIcon } from "./icons/modificationIcon.svg";
import { ReactComponent as MoonIcon } from "./icons/moonIcon.svg";
import { ReactComponent as PauseIcon } from "./icons/pauseIcon.svg";
import { ReactComponent as PencilIcon } from "./icons/pencilIcon.svg";
import { ReactComponent as PlayIcon } from "./icons/playIcon.svg";
import { ReactComponent as PlusIcon } from "./icons/plusIcon.svg";
import { ReactComponent as RotateIcon } from "./icons/rotateIcon.svg";

export type IconType =
  | "arrowRight"
  | "credits"
  | "cross"
  | "docs"
  | "ga"
  | "info"
  | "minus"
  | "modification"
  | "moon"
  | "pause"
  | "pencil"
  | "play"
  | "plus"
  | "rotate";

export interface IconProps {
  type: IconType;
  className?: string;
  height?: number | string;
  width?: number | string;
  // We need to consider the implementation of a mechanism with predefined colors and sizes
  // https://github.com/airbytehq/airbyte/issues/20133
}

export const Icons: Record<IconType, React.FC<React.SVGProps<SVGSVGElement>>> = {
  arrowRight: ArrowRightIcon,
  credits: CreditsIcon,
  cross: CrossIcon,
  docs: DocsIcon,
  ga: GAIcon,
  info: InfoIcon,
  minus: MinusIcon,
  modification: ModificationIcon,
  moon: MoonIcon,
  pause: PauseIcon,
  pencil: PencilIcon,
  play: PlayIcon,
  plus: PlusIcon,
  rotate: RotateIcon,
};
