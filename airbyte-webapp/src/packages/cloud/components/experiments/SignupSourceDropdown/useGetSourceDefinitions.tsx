import { SourceDefinitionRead } from "core/request/AirbyteClient";

import cloudCatalog from "./cloud_catalog.json";
import availableSourceDefinitions from "./sourceDefinitions.json";

// TODO/FIXME: we can enable this when we can access the bucket.
// interface Catalog {
//   destinations: DestinationDefinitionRead[];
//   sources: SourceDefinitionRead[];
// }
// const fetchCatalog = async (): Promise<Catalog> => {
//   const path = "https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/cloud_catalog.json";
//   const response = await fetch(path);
//   return response.json();
// };
// export const useGetSourceDefinitions = () => {
//   return useQuery<Catalog, Error, Catalog["sources"]>("cloud_catalog", fetchCatalog, {
//     select: (data) => {
//       return data.sources.map((source) => {
//         const icon = availableSourceDefinitions.sourceDefinitions.find(
//           (src) => src.sourceDefinitionId === source.sourceDefinitionId
//         )?.icon;
//         return {
//           ...source,
//           icon,
//         };
//       });
//     },
//   });
// };

// FIXME: For now, we relate on jsonn data copied from the request
export const mapSourcesWithIcons = (): SourceDefinitionRead[] => {
  return (cloudCatalog.sources as SourceDefinitionRead[]).map((source) => {
    const icon = availableSourceDefinitions.sourceDefinitions.find(
      (src) => src.sourceDefinitionId === source.sourceDefinitionId
    )?.icon;
    return {
      ...source,
      icon,
    };
  });
};
