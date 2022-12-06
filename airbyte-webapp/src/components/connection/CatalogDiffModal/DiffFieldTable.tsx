import { FormattedMessage } from "react-intl";

import { FieldTransform } from "core/request/AirbyteClient";

import styles from "./DiffFieldTable.module.scss";
import { DiffHeader } from "./DiffHeader";
import { FieldRow } from "./FieldRow";
import { DiffVerb } from "./types";

interface DiffFieldTableProps {
  fieldTransforms: FieldTransform[];
  diffVerb: DiffVerb;
}

export const DiffFieldTable: React.FC<DiffFieldTableProps> = ({ fieldTransforms, diffVerb }) => {
  return (
    <table className={styles.table} aria-label={`${diffVerb} fields`}>
      <thead>
        <tr className={styles.header}>
          <th>
            <DiffHeader diffCount={fieldTransforms.length} diffVerb={diffVerb} diffType="field" />
          </th>
          {diffVerb === "changed" && (
            <th>
              <FormattedMessage id="connection.updateSchema.dataType" />
            </th>
          )}
        </tr>
      </thead>
      <tbody>
        {fieldTransforms.map((transform) => {
          return <FieldRow transform={transform} key={`${transform.fieldName}.${transform.transformType}`} />;
        })}
      </tbody>
    </table>
  );
};
