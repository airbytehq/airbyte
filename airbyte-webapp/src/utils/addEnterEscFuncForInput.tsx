import * as React from "react";

export default function addEnterEscFuncForInput(WrapperComponent: React.FC) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return (props: any) => {
    const onKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
      // Escape Key Event
      if (event.key === "Escape") {
        if (props.onEscape) {
          props.onEscape(event);
        }
      }

      // Enter Key Event
      if (event.key === "Enter") {
        if (props.onEnter) {
          props.onEnter(event);
        }
      }

      if (props.onKeyDown) {
        props.onKeyDown(event);
      }
    };

    return <WrapperComponent {...props} onKeyDown={onKeyDown} />;
  };
}
