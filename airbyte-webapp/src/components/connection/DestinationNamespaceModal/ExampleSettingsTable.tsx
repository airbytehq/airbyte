import React from "react";

import { Text } from "components/ui/Text";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";

import styles from "./ExampleSettingsTable.module.scss";
import { useExampleTableData } from "./useExampleSettingsTable";

interface ExampleSettingsTableProps {
  namespaceDefinitionType: NamespaceDefinitionType;
}

export const ExampleSettingsTable: React.FC<ExampleSettingsTableProps> = ({ namespaceDefinitionType }) => {
  const { columns, data } = useExampleTableData(namespaceDefinitionType);

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
