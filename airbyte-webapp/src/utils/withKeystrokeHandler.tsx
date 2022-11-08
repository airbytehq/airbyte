import * as React from "react";

interface InProps {
  readonly onKeyDown?: React.KeyboardEventHandler<HTMLInputElement>;
}

interface Callbacks {
  readonly onEscape?: (event: React.KeyboardEvent<HTMLInputElement>) => void;
  readonly onEnter?: (event: React.KeyboardEvent<HTMLInputElement>) => void;
}

export default function withKeystrokeHandler<PI extends InProps>(
  WrapperComponent: React.FC<PI>
): React.FC<PI & Callbacks> {
  const result: React.FC<PI & Callbacks> = (props) => {
    const { onEscape, onEnter, ...restProps } = props;

    const onKeyDown = (event: React.KeyboardEvent<HTMLInputElement>): void => {
      if (event.key === "Escape" && onEscape) {
        onEscape(event);
      }

      if (event.key === "Enter" && onEnter) {
        onEnter(event);
      }

      if (props.onKeyDown) {
        props.onKeyDown(event);
      }
    };

    return <WrapperComponent {...(restProps as PI)} onKeyDown={onKeyDown} />;
  };

  result.displayName = `${WrapperComponent.displayName}WithKeystrokeHandler`;

  return result;
}
