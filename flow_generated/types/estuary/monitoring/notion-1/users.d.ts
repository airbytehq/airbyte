
// Generated from collection schema estuary/monitoring/notion-1/users.schema.yaml.
// Referenced from estuary/monitoring/notion-1/flow.yaml#/collections/estuary~1monitoring~1notion-1~1users.
export type Document = {
    avatar_url?: string | null;
    bot?: {
        owner?: {
            type?: string;
            workspace?: boolean | null;
        };
        [k: string]: unknown | undefined;
    } | null;
    id: string;
    name?: string;
    object?: "user";
    person?: {
        email?: string;
        [k: string]: unknown | undefined;
    } | null;
    type?: "bot" | "person";
    [k: string]: unknown | undefined;
};

