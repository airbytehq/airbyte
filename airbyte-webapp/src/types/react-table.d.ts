import "@tanstack/react-table";

/**
 * This extends to ColumnMeta interface to support optional <th/> and <td/> styling
 * More info: https://tanstack.com/table/v8/docs/api/core/table#meta
 * Undocumented 'meta' access: https://github.com/TanStack/table/issues/3983#issuecomment-1142334750
 */
declare module "@tanstack/table-core" {
  interface ColumnMeta {
    thClassName?: string;
    tdClassName?: string;
  }
}
