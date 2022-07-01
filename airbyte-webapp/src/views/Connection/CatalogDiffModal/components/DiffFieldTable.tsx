import { FieldTransform } from "core/request/AirbyteClient";

import styles from "./DiffFieldTable.module.scss";
import { DiffHeader, DiffVerb } from "./DiffHeader";
import { FieldRow } from "./FieldRow";

interface DiffFieldTableProps {
  fieldTransforms: FieldTransform[];
  diffVerb: DiffVerb;
}

export const DiffFieldTable: React.FC<DiffFieldTableProps> = ({ fieldTransforms, diffVerb }) => {
  return (
    <table>
      <thead>
        <tr className={styles.accordionSubHeader}>
          <th>
            <DiffHeader diffCount={fieldTransforms.length} diffVerb={diffVerb} diffType="field" />
          </th>
          {diffVerb === "changed" && <th>Data type</th>}
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
