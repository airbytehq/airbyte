import { AirbyteCatalog, FieldTransform, StreamTransform } from "core/request/AirbyteClient";

interface CatalogDiffRow {
  item: FieldTransform | StreamTransform;
  catalog: AirbyteCatalog;
  children?: React.ReactChild;
}

export const CatalogDiffRow: React.FC<CatalogDiffRow> = ({ item }) => {
  // if it's a stream, get the catalog data
  // if it's a field, get the field type

  // render the row!
  return <></>;
};
