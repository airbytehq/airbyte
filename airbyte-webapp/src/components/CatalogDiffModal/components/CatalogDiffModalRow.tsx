import { AirbyteCatalog, FieldTransform, StreamTransform } from "core/request/AirbyteClient";

interface CatalogDiffModalRow {
  item: FieldTransform | StreamTransform;
  catalog: AirbyteCatalog;
  children?: React.ReactChild;
}

export const CatalogDiffModalRow: React.FC<CatalogDiffModalRow> = ({ item }) => {
  // if it's a stream, get the catalog data
  // if it's a field, get the field type

  // render the row!
  return <></>;
};
