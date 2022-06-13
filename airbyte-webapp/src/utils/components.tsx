import classNamesBuilder, { Argument } from "classnames";
import React, { useMemo } from "react";

export function classy<P, T extends HTMLElement = HTMLElement>(
  type: keyof Omit<React.ReactHTML, "input">,
  classNames?: Argument | ((props: P) => Argument)
): React.FC<React.HTMLAttributes<T> & P>;

// export function classy<P extends React.InputHTMLAttributes<T>, T extends HTMLInputElement>(
//   type: "input",
//   classNames?: Argument | ((props: P) => Argument)
// ): React.FC<React.InputHTMLAttributes<T>>;

// export function classy<P = Record<string, unknown>>(
//   type: React.FC<P>,
//   classNames?: Argument | ((props: P) => Argument)
// ): React.FC<P>;

export function classy<T, P>(
  type: keyof React.ReactHTML | React.FC<P>,
  classNames?: Argument | ((props: P) => Argument)
): React.FC<(React.HTMLAttributes<T> & P) | (P & { className: string })> {
  return (props) => {
    const className = useMemo(() => {
      const baseClassNames = typeof classNames === "function" ? classNames?.(props) : classNames;
      return classNamesBuilder(baseClassNames, props.className);
    }, [props]);

    return React.createElement(type, { ...props, className }, props.children);
  };
}
