export interface DeleteBlockProps {
  type: "source" | "destination" | "connection";
  onDelete: () => Promise<unknown>;
}
