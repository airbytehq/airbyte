import classNames, { Argument } from "classnames";
import React, { useMemo } from "react";

export const classy =
  <T extends HTMLElement, P = Record<string, never>>(
    type: keyof React.ReactHTML,
    classNameGenerator?: Argument | ((props: P) => Argument)
  ): React.FC<React.HTMLAttributes<T> & P> =>
  (props) => {
    const className = useMemo(() => {
      const generatedClassNames =
        typeof classNameGenerator === "function" ? classNameGenerator?.(props) : classNameGenerator;
      return classNames(generatedClassNames, props.className);
    }, [props]);

    return React.createElement(type, { ...props, className }, props.children);
  };
