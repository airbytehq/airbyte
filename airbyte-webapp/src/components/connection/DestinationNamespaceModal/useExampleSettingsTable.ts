import { useIntl } from "react-intl";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";

export const useExampleTableData = (
  namespaceDefinition: NamespaceDefinitionType
): {
  columns: Array<{ id: string; displayName: string }>;
  data: Array<Record<string, string>>;
} => {
  const { formatMessage } = useIntl();

  switch (namespaceDefinition) {
    case NamespaceDefinitionType.source:
      return {
        columns: [
          {
            id: "sourceNamespace",
            displayName: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.header.sourceNamespace",
            }),
          },
          {
            id: "destinationNamespace",
            displayName: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.header.destinationNamespace",
            }),
          },
        ],
        data: [
          {
            sourceNamespace: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.data.public",
            }),
            destinationNamespace: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.data.public",
            }),
          },
          {
            sourceNamespace: "",
            destinationNamespace: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.data.mySchema",
            }),
          },
        ],
      };
    case NamespaceDefinitionType.destination:
      return {
        columns: [
          {
            id: "sourceNamespace",
            displayName: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.header.sourceNamespace",
            }),
          },
          {
            id: "destinationNamespace",
            displayName: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.header.destinationNamespace",
            }),
          },
        ],
        data: [
          {
            sourceNamespace: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.data.public",
            }),
            destinationNamespace: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.data.mySchema",
            }),
          },
          {
            sourceNamespace: "",
            destinationNamespace: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.data.mySchema",
            }),
          },
        ],
      };
    case NamespaceDefinitionType.customformat:
      return {
        columns: [
          {
            id: "customFormat",
            displayName: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.header.customFormat",
            }),
          },
          {
            id: "sourceNamespace",
            displayName: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.header.sourceNamespace",
            }),
          },
          {
            id: "destinationNamespace",
            displayName: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.header.destinationNamespace",
            }),
          },
        ],
        data: [
          {
            customFormat: formatMessage(
              {
                id: "connectionForm.modal.destinationNamespace.table.data.custom",
              },
              { symbol: (node: React.ReactNode) => `"${node}"` }
            ),
            sourceNamespace: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.data.public",
            }),
            destinationNamespace: formatMessage(
              {
                id: "connectionForm.modal.destinationNamespace.table.data.custom",
              },
              { symbol: (node: React.ReactNode) => `${node}` }
            ),
          },
          {
            customFormat: formatMessage(
              {
                id: "connectionForm.modal.destinationNamespace.table.data.exampleSourceNamespace",
              },
              { symbol: (node: React.ReactNode) => `{${node}}` }
            ),
            sourceNamespace: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.data.public",
            }),
            destinationNamespace: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.data.public",
            }),
          },
          {
            customFormat: formatMessage(
              {
                id: "connectionForm.modal.destinationNamespace.table.data.exampleMySourceNamespace",
              },
              { symbol: (node: React.ReactNode) => `{${node}}` }
            ),
            sourceNamespace: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.data.public",
            }),
            destinationNamespace: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.data.myPublicSchema",
            }),
          },
          {
            customFormat: "",
            sourceNamespace: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.data.public",
            }),
            destinationNamespace: formatMessage({
              id: "connectionForm.modal.destinationNamespace.table.data.mySchema",
            }),
          },
        ],
      };
  }
};
