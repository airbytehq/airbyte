import classNamesBuilder, { Argument } from "classnames";
import React, { useMemo } from "react";

export function classy<T extends HTMLElement, P = Record<string, never>>(
  type: keyof React.ReactHTML,
  classNames?: Argument | ((props: P) => Argument)
): React.FC<React.HTMLAttributes<T> & P>;

export function classy<T extends HTMLElement, P = Record<string, never>>(
  type: "input",
  classNames?: Argument | ((props: P) => Argument)
): React.FC<React.InputHTMLAttributes<T> & P>;

export function classy<P = Record<string, never>>(
  type: React.FC<P>,
  classNames?: Argument | ((props: P) => Argument)
): React.FC<P>;

export function classy<T extends HTMLElement, P = Record<string, never>>(
  type: keyof React.ReactHTML | "input" | React.FC<P>,
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
