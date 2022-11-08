import { useIntl } from "react-intl";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";

interface NamespaceOptions {
  namespaceDefinition:
    | typeof NamespaceDefinitionType.source
    | typeof NamespaceDefinitionType.destination
    | typeof NamespaceDefinitionType.customformat;
  namespaceFormat?: string;
}

export const useDestinationNamespace = (opt: NamespaceOptions): string | undefined => {
  const { formatMessage } = useIntl();

  switch (opt.namespaceDefinition) {
    case NamespaceDefinitionType.source:
      return formatMessage({ id: "connection.catalogTree.sourceSchema" });
    case NamespaceDefinitionType.destination:
      return formatMessage({ id: "connection.catalogTree.destinationSchema" });
    case NamespaceDefinitionType.customformat:
      return opt.namespaceFormat;
  }
};
