import { FieldTransform } from "core/request/AirbyteClient";

import styles from "./DiffFieldTable.module.scss";
import { DiffHeader } from "./DiffHeader";

interface DiffFieldTableProps {
  fieldTransforms: FieldTransform[];
}

export const DiffFieldTable: React.FC<DiffFieldTableProps> = ({ fieldTransforms }) => {
  return (
    <table>
      <tr className={styles.accordionSubHeader}>
        <th>
          <DiffHeader diffCount={fieldTransforms.length} diffVerb="new" diffType="field" />
        </th>
        <th>Data type</th>
      </tr>
    </table>
  );
};
