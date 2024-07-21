from typing import Optional

from destination_palantir_foundry.foundry_api.compass import Compass, DecoratedResource


class ProjectHelper:
    def __init__(self, compass: Compass):
        self.compass = compass

    def maybe_get_resource_by_name(self, project_rid: str, resource_name: str) -> Optional[DecoratedResource]:
        rids_to_paths = self.compass.get_paths([project_rid])
        parent_path = rids_to_paths.root.get(project_rid)
        if parent_path is None:
            raise ValueError(
                f"Could not resolve path for project {project_rid}. Please ensure the project exists and that the client has access to it.")

        return self.compass.get_resource_by_path(f"{parent_path}/{resource_name}").root
