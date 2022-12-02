import { MessageDescriptor } from "react-intl";

export const getTableData = (formatMsgCb: (msg: MessageDescriptor) => string): Array<Record<string, string>> => [
  {
    sourceNamespace: formatMsgCb({
      id: "connectionForm.modal.destinationNamespace.table.data.public",
    }),
    destinationNamespace: formatMsgCb({
      id: "connectionForm.modal.destinationNamespace.table.data.public",
    }),
  },
  {
    sourceNamespace: "",
    destinationNamespace: formatMsgCb({
      id: "connectionForm.modal.destinationNamespace.table.data.mySchema",
    }),
  },
];
