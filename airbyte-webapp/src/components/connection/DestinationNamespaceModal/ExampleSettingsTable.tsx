import React from "react";

import { Text } from "../../ui/Text";
import styles from "./ExampleSettingsTable.module.scss";

export interface ExampleSettingsTableProps {
  columns: Array<{ id: string; displayName: string }>;
  data: Array<Record<string, string>>;
}

export const ExampleSettingsTable: React.FC<ExampleSettingsTableProps> = ({ columns, data }) => {
  return (
    <table className={styles.exampleSettingsTable}>
      <thead>
        <tr>
          {columns.map((column, index) => (
            <th key={`column_${index}`}>
              <Text className={styles.text} size="xs">
                {column.displayName}
              </Text>
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, rowIndex) => (
          <tr key={`row_${rowIndex}`}>
            {columns.map((column, dataIndex) => (
              <td key={`dataIndex_${dataIndex}`}>
                <Text size="xs">{row[column.id]}</Text>
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};
