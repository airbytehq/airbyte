import * as React from "react";

export default function addEnterEscFuncForInput(WrapperComponent: React.FC) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return (props: any) => {
    const { onEscape, onEnter, ...restProps } = props;

    const onKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
      // Escape Key Event
      if (event.key === "Escape" && onEscape) {
        onEscape(event);
      }

      // Enter Key Event
      if (event.key === "Enter" && onEnter) {
        onEnter(event);
      }

      if (props.onKeyDown) {
        props.onKeyDown(event);
      }
    };

    return <WrapperComponent {...restProps} onKeyDown={onKeyDown} />;
  };
}
