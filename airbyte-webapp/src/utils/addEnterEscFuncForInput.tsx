import * as React from "react";

export default function addEnterEscFuncForInput(WrapperComponent: React.FC) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return ({ onEscape, onEnter, onKeyDown: onKeyDownProp, ...props }: any) => {
    const onKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
      // Escape Key Event
      if (event.key === "Escape" && onEscape) {
        onEscape(event);
      }

      // Enter Key Event
      if (event.key === "Enter" && onEnter) {
        onEnter(event);
      }

      onKeyDownProp?.(event);
    };

    return <WrapperComponent {...props} onKeyDown={onKeyDown} />;
  };
}
