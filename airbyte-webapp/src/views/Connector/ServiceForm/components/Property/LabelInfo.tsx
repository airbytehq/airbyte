import React from "react";

import { TextWithHTML } from "components";

import styles from "./LabelInfo.module.scss";
import { JSONSchema7Type } from "json-schema";

interface IProps {
  label: React.ReactNode;
  examples?: JSONSchema7Type;
  description?: string;
}

const LabelInfo: React.FC<IProps> = ({ label, examples, description }) => {
  const constructExamples = () => {
    if (!examples) {
      return null;
    }

    const examplesArray = Array.isArray(examples) ? examples : [examples];

    return (
      <>
        {/* don't use <Text as=h4> here, because we want the default tooltip text styling for this header */}
        <h4 className={styles.exampleHeader}>{`Example value${examplesArray.length > 1 ? "s" : ""}`}</h4>
        <div className={styles.exampleContainer}>
          {examplesArray.map((example) => (
            <span className={styles.exampleItem}>{example}</span>
          ))}
        </div>
      </>
    );
  };

  return (
    <>
      <h4 className={styles.descriptionHeader}>{label}</h4>
      {description && <TextWithHTML text={description} />}
      {constructExamples()}
    </>
  );
};

export { LabelInfo };
