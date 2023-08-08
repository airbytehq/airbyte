"""CI Workflow for Airbyte Java CDK"""

from aircmd.models.click_commands import ClickGroup
from aircmd.models.plugins import DeveloperPlugin

from cdk.java_cdk.ci import java_group

cdk_plugin = DeveloperPlugin(name="cdk", base_dirs=["airbyte"])
cdk_group = ClickGroup(group_name="cdk", group_help="Commands for developing Airbyte CDK")

cdk_group.add_group(java_group)
cdk_plugin.add_group(cdk_group)
