import { useField } from "formik";
import React, { ReactElement, useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";

import styles from "./BuilderList.module.scss";

interface BuilderListProps {
  children: (props: { buildPath: (path: string) => string }) => ReactElement;
  basePath: string;
  onDelete: (index: number) => void;
  onAdd: () => void;
}

export const BuilderList: React.FC<BuilderListProps> = ({ children, onDelete, basePath, onAdd }) => {
  const [list] = useField<unknown[]>(basePath);

  const buildPathFunctions = useMemo(
    () =>
      new Array(list.value.length).fill(undefined).map((_value, index) => {
        return (path: string) => `${basePath}[${index}].${path}`;
      }),
    [basePath, list.value.length]
  );

  return (
    <>
      {buildPathFunctions.map((buildPath, index) => (
        <div className={styles.item}>
          {children({ buildPath })}
          <Button variant="danger" onClick={() => onDelete(index)}>
            <FormattedMessage id="form.delete" />
          </Button>
        </div>
      ))}
      <div>
        <Button onClick={onAdd}>
          <FormattedMessage id="form.add" />
        </Button>
      </div>
    </>
  );
};
