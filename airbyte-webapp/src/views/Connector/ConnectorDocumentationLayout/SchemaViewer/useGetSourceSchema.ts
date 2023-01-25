import { JSONSchema4 } from "json-schema";
import { useQuery } from "react-query";

import { useConfig } from "packages/cloud/services/config";

const fetchSchema = async ({
  apiUrl,
  sourceDefinitionId,
}: {
  apiUrl: string;
  sourceDefinitionId: string;
}): Promise<JSONSchema4> => {
  const path = `${apiUrl}/source_definition/${sourceDefinitionId}/discover_schema`;

  const response = await fetch(path);

  if (!response.ok) {
    throw new Error("Schema not found");
  }
  return response.json();
};

export const useGetSourceSchema = ({ sourceDefinitionId }: { sourceDefinitionId: string }) => {
  const { cloudNodeApiUrl: apiUrl } = useConfig();

  return useQuery({
    queryKey: ["schema", sourceDefinitionId],
    queryFn: () => fetchSchema({ apiUrl, sourceDefinitionId }),
    staleTime: 24 * 60 * 60,
    retry: false,
    select: (data) => {
      // Just to be safe, in case a stream does not have any properties. This could  happen when we haven't infer the $ref correctly
      Object.keys(data).forEach((key) => {
        if (!data[key].properties) {
          delete data[key];
        }
      });
      return data;
    },
  });
};
