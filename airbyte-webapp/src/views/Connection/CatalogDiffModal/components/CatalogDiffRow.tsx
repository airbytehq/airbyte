import { AirbyteCatalog, FieldTransform, StreamTransform } from "core/request/AirbyteClient";

interface CatalogDiffRowProps {
  item: FieldTransform | StreamTransform;
  catalog: AirbyteCatalog;
}

export const CatalogDiffRow: React.FC<CatalogDiffRowProps> = ({}) => {
  // if it's a stream, get the catalog data
  // if it's a field, get the field type

  // render the row!
  // use the transformType to use classnames to apply condiitonal styling
  return (
    <div>
      {/* {tableName} {item.transformType === "add_stream" ? syncMode : item.transformType.includes("field") ? fieldType ?? null} */}
    </div>
  );
};
