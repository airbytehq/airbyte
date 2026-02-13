import { API_SIDEBAR_PATH, SPEC_CACHE_PATH } from "./constants";
import * as fs from "fs";

const loadAllowedTags = (): string[] => {
  if (fs.existsSync(SPEC_CACHE_PATH)) {
    try {
      const spec = JSON.parse(fs.readFileSync(SPEC_CACHE_PATH, "utf8"));
      return spec.tags?.map((tag: any) => tag.name) || [];
    } catch (e) {
      console.warn("Could not load OpenAPI spec for tag filtering:", e);
    }
  }
  return [];
};

interface AgentEngineApiSidebar {
  items: any[];
  introDocId?: string;
}

export const loadAgentEngineApiSidebar = (): AgentEngineApiSidebar => {
  const allowedTags = loadAllowedTags();

  if (fs.existsSync(API_SIDEBAR_PATH)) {
    try {
      const sidebarModule = require(API_SIDEBAR_PATH);
      const allItems = sidebarModule.default || sidebarModule || [];

      // Find the intro doc (type: "doc" at the top level, not inside a category)
      const introItem = allItems.find(
        (item: any) => item.type === "doc" && !item.label,
      );
      const introDocId = introItem?.id;

      // Filter out the intro doc from items and keep only allowed tag categories
      const filteredItems = allItems.filter((item: any) => {
        if (item.type === "doc" && item === introItem) {
          return false;
        }
        if (item.type === "category") {
          return allowedTags.includes(item.label);
        }
        return true;
      });

      console.log(`Filtered API sidebar to ${filteredItems.length} items`);
      return { items: filteredItems, introDocId };
    } catch (e) {
      console.warn("Could not load pre-generated API sidebar:", e);
      return { items: [] };
    }
  }
  return { items: [] };
};

// Helper function to find and replace the "api-reference" category
export const replaceApiReferenceCategory = (
  items: any[],
  agentEngineApiSidebar: AgentEngineApiSidebar,
): any[] => {
  return items.map((item) => {
    if (
      item.type === "category" &&
      item.label === "api-reference" &&
      item.items !== undefined
    ) {
      const categoryProps: any = {
        ...item,
        label: "Agent Engine API Reference",
        items: agentEngineApiSidebar.items,
      };

      if (agentEngineApiSidebar.introDocId) {
        categoryProps.link = {
          type: "doc",
          id: agentEngineApiSidebar.introDocId,
        };
      }

      return categoryProps;
    }

    if (item.items) {
      return {
        ...item,
        items: replaceApiReferenceCategory(item.items, agentEngineApiSidebar),
      };
    }

    return item;
  });
};
