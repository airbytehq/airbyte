import React from "react";

import { TextWithHTML } from "components";

import { FormBaseItem } from "core/form/types";

import styles from "./LabelInfo.module.scss";

interface IProps {
  property: FormBaseItem;
  label: React.ReactNode;
}

const LabelInfo: React.FC<IProps> = ({ property, label }) => {
  const constructExamples = () => {
    if (!property.examples) {
      return null;
    }

    const examplesArray = Array.isArray(property.examples) ? property.examples : [property.examples];

    return (
      <>
        {/* don't use <Text as=h4> here, because we want the default tooltip styling for this header */}
        <h4 className={styles.exampleHeader}>{`Example value${examplesArray.length > 1 ? "s" : ""}`}</h4>
        <ul className={styles.exampleList}>
          {examplesArray.map((example) => (
            <li key={example?.toString()}>{example}</li>
          ))}
        </ul>
      </>
    );
  };

  const description = property.description ? <TextWithHTML text={property.description} /> : null;

  return (
    <>
      <h4 className={styles.descriptionHeader}>{label}</h4>
      {description}
      {constructExamples()}
    </>
  );
};

export { LabelInfo };
