import React from "react";

import { TextWithHTML } from "components";

import { FormBaseItem } from "core/form/types";

import styles from "./LabelInfo.module.scss";

interface IProps {
  property: FormBaseItem;
  error: string | undefined;
  touched: boolean;
}

const LabelInfo: React.FC<IProps> = ({ property }) => {
  const constructExamples = () => {
    if (!property.examples) {
      return null;
    }

    const examplesArray = Array.isArray(property.examples) ? property.examples : [property.examples];

    return (
      <>
        {/* don't use <Text as=h4> here, because we want the default tooltip styling for this header */}
        <h4 className={styles.exampleHeader}>{examplesArray.length > 1 ? "Examples" : "Example"}</h4>
        <ul className={styles.exampleList}>
          {examplesArray.map((example) => (
            <li>{example}</li>
          ))}
        </ul>
      </>
    );
  };

  const message = property.description ? <TextWithHTML text={property.description} /> : null;

  return (
    <>
      {message}
      {constructExamples()}
    </>
  );
};

export { LabelInfo };
