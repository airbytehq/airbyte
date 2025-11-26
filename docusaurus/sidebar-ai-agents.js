import fs from "fs";
import apiSidebarItems from "../docs/ai-agents/embedded/api-reference/sidebar.ts";

// Path to the cached embedded API OpenAPI specification
const SPEC_CACHE_PATH = "./src/data/embedded_api_spec.json";

/**
 * Load the allowed tags from the OpenAPI spec.
 * Only tags explicitly defined in the spec's top-level `tags` array should be shown in the sidebar.
 * This filters out tags that are only assigned to operations but not formally defined.
 */
function loadAllowedTags() {
  try {
    const specJson = JSON.parse(fs.readFileSync(SPEC_CACHE_PATH, "utf8"));
    return specJson.tags?.map((tag) => tag.name) ?? [];
  } catch (e) {
    console.warn("Could not load embedded API spec for sidebar filtering:", e);
    return null; // fall back to no filtering if something goes wrong
  }
}

/**
 * Filter sidebar items to only include categories whose label matches an allowed tag.
 * Non-category items (like docs) are always included.
 */
function filterSidebarByTags(items, allowedTags) {
  if (!allowedTags) return items; // graceful fallback if spec couldn't be loaded
  return items.filter((item) => {
    if (item.type !== "category") return true;
    return allowedTags.includes(item.label);
  });
}

// Helper function to add unique keys to sidebar items to avoid duplicate translation key errors
// The generated sidebar already has correct IDs, we just need to add unique keys
function addUniqueKeys(items) {
  return items.map((item) => {
    if (item.type === "doc") {
      return {
        ...item,
        // Use the doc id as a unique translation key
        key: item.id,
      };
    }

    if (item.type === "category") {
      return {
        ...item,
        // Make categories unique too using their link id or label
        key: item.link?.id || item.label,
        items: item.items ? addUniqueKeys(item.items) : [],
      };
    }

    return item;
  });
}

// Load allowed tags from the OpenAPI spec and filter the sidebar items
const allowedTags = loadAllowedTags();
const filteredSidebar = filterSidebarByTags(apiSidebarItems, allowedTags);

// Get the generated API sidebar items with unique keys
// Skip the first item (sonar overview) since we use it as the category link
const [, ...apiSidebarItemsWithKeys] = addUniqueKeys(filteredSidebar);

export default {
  "ai-agents": [
    {
      type: "category",
      collapsible: false,
      label: "AI Agents",
      link: {
        type: "doc",
        id: "README",
      },
      items: [
        {
          type: "category",
          label: "Embedded",
          items: [
            {
              type: "category",
              label: "Widget",
              items: [
                "embedded/widget/quickstart",
                {
                  type: "category",
                  label: "Tutorials",
                  items: [
                    "embedded/widget/tutorials/prerequisites-setup",
                    "embedded/widget/tutorials/develop-your-app",
                    "embedded/widget/tutorials/use-embedded",
                  ],
                },
                "embedded/widget/managing-embedded",
                "embedded/widget/template-tags",
              ],
            },
            {
              type: "category",
              label: "API",
              items: [
                "embedded/api/README",
                {
                  type: "category",
                  label: "Sonar API Reference",
                  link: {
                    type: "doc",
                    id: "embedded/api-reference/sonar",
                  },
                  items: apiSidebarItemsWithKeys,
                },
                "embedded/api/connection-templates",
                "embedded/api/source-templates",
                "embedded/api/configuring-sources",
              ],
            },
          ],
        },
        {
          type: "category",
          label: "MCP Servers",
          items: [
            {
              type: "doc",
              id: "pyairbyte-mcp",
              label: "PyAirbyte MCP",
            },
            {
              type: "doc",
              id: "connector-builder-mcp",
              label: "Connector Builder MCP",
            },
            {
              type: "doc",
              id: "embedded/operator-mcp/README",
              label: "Embedded Operator MCP",
            }
          ]
        }
      ]
    }
  ],
};
