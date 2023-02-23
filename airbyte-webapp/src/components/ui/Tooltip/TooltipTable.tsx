import { useTooltipContext } from "./context";
import styles from "./TooltipTable.module.scss";

interface TooltipTableProps {
  rows: React.ReactNode[][];
}

export const TooltipTable: React.FC<TooltipTableProps> = ({ rows }) => {
  const { theme } = useTooltipContext();

  return rows.length > 0 ? (
    <table className={theme === "light" ? styles.light : undefined}>
      <tbody>
        {rows?.map((cols) => (
          <tr>
            {cols.map((col, index) => (
              <td className={index === 0 ? styles.label : undefined}>{col}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  ) : null;
};
