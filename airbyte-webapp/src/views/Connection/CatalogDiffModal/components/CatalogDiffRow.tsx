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
  // use the transformType to use classnames to apply condiitonal styling
  return (
    <div>
      {item}
      {/* {tableName} {item.transformType === "add_stream" ? syncMode : item.transformType.includes("field") ? fieldType ?? null} */}
    </div>
  );
};
