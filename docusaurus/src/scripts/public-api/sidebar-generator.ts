import { API_SIDEBAR_PATH } from "./constants";
import * as fs from "fs";

interface PublicApiSidebar {
  items: any[];
}

const addSidebarKeys = (items: any[], parentKey = "public-api"): any[] =>
  items.map((item, index) => {
    const itemKey = `${parentKey}-${item.id || item.label || index}`;

    if (item.type === "category") {
      return {
        ...item,
        key: item.key || itemKey,
        items: addSidebarKeys(item.items || [], itemKey),
      };
    }

    return {
      ...item,
      key: item.key || itemKey,
    };
  });

export const loadPublicApiSidebar = (): PublicApiSidebar => {
  if (!fs.existsSync(API_SIDEBAR_PATH)) {
    return { items: [] };
  }

  try {
    const sidebarModule = require(API_SIDEBAR_PATH);
    const sidebar = sidebarModule.default || sidebarModule;
    return {
      items: addSidebarKeys(
        Array.isArray(sidebar) ? sidebar : sidebar.apisidebar || [],
      ),
    };
  } catch (error) {
    console.warn("Could not load pre-generated public API sidebar:", error);
    return { items: [] };
  }
};
