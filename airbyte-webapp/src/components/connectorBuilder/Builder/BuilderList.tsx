import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useField } from "formik";
import React, { ReactElement, useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";

import styles from "./BuilderList.module.scss";
import { RemoveButton } from "./RemoveButton";

interface BuilderListProps {
  children: (props: { buildPath: (path: string) => string }) => ReactElement;
  basePath: string;
  emptyItem: object;
}

export const BuilderList: React.FC<BuilderListProps> = ({ children, emptyItem, basePath }) => {
  const [list, , helpers] = useField<object[]>(basePath);

  const buildPathFunctions = useMemo(
    () =>
      new Array(list.value.length).fill(undefined).map((_value, index) => {
        return (path: string) => `${basePath}[${index}]${path !== "" ? "." : ""}${path}`;
      }),
    [basePath, list.value.length]
  );

  return (
    <>
      {buildPathFunctions.map((buildPath, currentItemIndex) => (
        <div className={styles.itemWrapper} key={currentItemIndex}>
          <div className={styles.itemContainer}>{children({ buildPath })}</div>
          <RemoveButton
            onClick={() => {
              const updatedItems = list.value.filter((_, index) => index !== currentItemIndex);
              helpers.setValue(updatedItems);
            }}
          />
        </div>
      ))}
      <div>
        <Button
          variant="secondary"
          icon={<FontAwesomeIcon icon={faPlus} />}
          onClick={() => {
            helpers.setValue([...list.value, { ...emptyItem }]);
          }}
        >
          <FormattedMessage id="connectorBuilder.addNewSlicer" />
        </Button>
      </div>
    </>
  );
};
