import { CatalogDiff } from "core/request/AirbyteClient";

export const mockCatalogDiff: CatalogDiff = {
  transforms: [
    {
      transformType: "update_stream",
      streamDescriptor: { namespace: "apple", name: "harissa_paste" },
      updateStream: [
        { transformType: "add_field", fieldName: ["users", "phone"], breaking: false },
        { transformType: "add_field", fieldName: ["users", "email"], breaking: false },
        { transformType: "remove_field", fieldName: ["users", "lastName"], breaking: false },

        {
          transformType: "update_field_schema",
          breaking: false,
          fieldName: ["users", "address"],
          updateFieldSchema: { oldSchema: { type: "number" }, newSchema: { type: "string" } },
        },
      ],
    },
    {
      transformType: "add_stream",
      streamDescriptor: { namespace: "apple", name: "banana" },
    },
    {
      transformType: "add_stream",
      streamDescriptor: { namespace: "apple", name: "carrot" },
    },
    {
      transformType: "remove_stream",
      streamDescriptor: { namespace: "apple", name: "dragonfruit" },
    },
    {
      transformType: "remove_stream",
      streamDescriptor: { namespace: "apple", name: "eclair" },
    },
    {
      transformType: "remove_stream",
      streamDescriptor: { namespace: "apple", name: "fishcake" },
    },
    {
      transformType: "remove_stream",
      streamDescriptor: { namespace: "apple", name: "gelatin_mold" },
    },
  ],
};
