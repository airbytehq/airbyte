#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
import xml.dom
import xml.dom.minidom

#- Relevant constants from Windows headers
# Manifest resource code
RT_MANIFEST = 24

# Resource IDs (names) for manifest.
# See: https://www.gamedev.net/blogs/entry/2154553-manifest-embedding-and-activation
CREATEPROCESS_MANIFEST_RESOURCE_ID = 1
ISOLATIONAWARE_MANIFEST_RESOURCE_ID = 2

LANG_NEUTRAL = 0

#- Default application manifest template, based on the one found in python executable.

_DEFAULT_MANIFEST_XML = \
b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"></requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <supportedOS Id="{e2011457-1546-43c5-a5fe-008deee3d3f0}"></supportedOS>
      <supportedOS Id="{35138b9a-5d96-4fbd-8e2d-a2440225f93a}"></supportedOS>
      <supportedOS Id="{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}"></supportedOS>
      <supportedOS Id="{1f676c76-80e1-4239-95bb-83d0f6d0da78}"></supportedOS>
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"></supportedOS>
    </application>
  </compatibility>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <longPathAware xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">true</longPathAware>
    </windowsSettings>
  </application>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.Windows.Common-Controls" version="6.0.0.0" processorArchitecture="*" publicKeyToken="6595b64144ccf1df" language="*"></assemblyIdentity>
    </dependentAssembly>
  </dependency>
</assembly>
"""  # noqa: E501

#- DOM navigation helpers


def _find_elements_by_tag(root, tag):
    """
    Find all elements with given tag under the given root element.
    """
    return [node for node in root.childNodes if node.nodeType == xml.dom.Node.ELEMENT_NODE and node.tagName == tag]


def _find_element_by_tag(root, tag):
    """
    Attempt to find a single element with given tag under the given root element, and return None if no such element
    is found. Raises an error if multiple elements are found.
    """
    elements = _find_elements_by_tag(root, tag)
    if len(elements) > 1:
        raise ValueError(f"Expected a single {tag!r} element, found {len(elements)} element(s)!")
    if not elements:
        return None
    return elements[0]


#- Application manifest modification helpers


def _set_execution_level(manifest_dom, root_element, uac_admin=False, uac_uiaccess=False):
    """
    Find <security> -> <requestedPrivileges> -> <requestedExecutionLevel> element, and set its `level` and `uiAccess`
    attributes based on supplied arguments. Create the XML elements if necessary, as they are optional.
    """

    # <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    trust_info_element = _find_element_by_tag(root_element, "trustInfo")
    if not trust_info_element:
        trust_info_element = manifest_dom.createElement("trustInfo")
        trust_info_element.setAttribute("xmlns", "urn:schemas-microsoft-com:asm.v3")
        root_element.appendChild(trust_info_element)

    # <security>
    security_element = _find_element_by_tag(trust_info_element, "security")
    if not security_element:
        security_element = manifest_dom.createElement("security")
        trust_info_element.appendChild(security_element)

    # <requestedPrivileges>
    requested_privileges_element = _find_element_by_tag(security_element, "requestedPrivileges")
    if not requested_privileges_element:
        requested_privileges_element = manifest_dom.createElement("requestedPrivileges")
        security_element.appendChild(requested_privileges_element)

    # <requestedExecutionLevel>
    requested_execution_level_element = _find_element_by_tag(requested_privileges_element, "requestedExecutionLevel")
    if not requested_execution_level_element:
        requested_execution_level_element = manifest_dom.createElement("requestedExecutionLevel")
        requested_privileges_element.appendChild(requested_execution_level_element)

    requested_execution_level_element.setAttribute("level", "requireAdministrator" if uac_admin else "asInvoker")
    requested_execution_level_element.setAttribute("uiAccess", "true" if uac_uiaccess else "false")


def _ensure_common_controls_dependency(manifest_dom, root_element):
    """
    Scan <dependency> elements for the one whose <<dependentAssembly> -> <assemblyIdentity> corresponds to the
    `Microsoft.Windows.Common-Controls`. If found, overwrite its properties. If not, create new <dependency>
    element with corresponding sub-elements and attributes.
    """

    # <dependency>
    dependency_elements = _find_elements_by_tag(root_element, "dependency")
    for dependency_element in dependency_elements:
        # <dependentAssembly>
        dependent_assembly_element = _find_element_by_tag(dependency_element, "dependentAssembly")
        # <assemblyIdentity>
        assembly_identity_element = _find_element_by_tag(dependent_assembly_element, "assemblyIdentity")
        # Check the name attribute
        if assembly_identity_element.attributes["name"].value == "Microsoft.Windows.Common-Controls":
            common_controls_element = assembly_identity_element
            break
    else:
        # Create <dependency>
        dependency_element = manifest_dom.createElement("dependency")
        root_element.appendChild(dependency_element)
        # Create <dependentAssembly>
        dependent_assembly_element = manifest_dom.createElement("dependentAssembly")
        dependency_element.appendChild(dependent_assembly_element)
        # Create <assemblyIdentity>
        common_controls_element = manifest_dom.createElement("assemblyIdentity")
        dependent_assembly_element.appendChild(common_controls_element)

    common_controls_element.setAttribute("type", "win32")
    common_controls_element.setAttribute("name", "Microsoft.Windows.Common-Controls")
    common_controls_element.setAttribute("version", "6.0.0.0")
    common_controls_element.setAttribute("processorArchitecture", "*")
    common_controls_element.setAttribute("publicKeyToken", "6595b64144ccf1df")
    common_controls_element.setAttribute("language", "*")


def create_application_manifest(manifest_xml=None, uac_admin=False, uac_uiaccess=False):
    """
    Create application manifest, from built-in or custom manifest XML template. If provided, `manifest_xml` must be
    a string or byte string containing XML source. The returned manifest is a byte string, encoded in UTF-8.

    This function sets the attributes of `requestedExecutionLevel` based on provided `uac_admin` and `auc_uiacces`
    arguments (creating the parent elements in the XML, if necessary). It also scans `dependency` elements for the
    entry corresponding to `Microsoft.Windows.Common-Controls` and creates or modifies it as necessary.
    """

    if manifest_xml is None:
        manifest_xml = _DEFAULT_MANIFEST_XML

    with xml.dom.minidom.parseString(manifest_xml) as manifest_dom:
        root_element = manifest_dom.documentElement

        # Validate root element - must be <assembly>
        assert root_element.tagName == "assembly"
        assert root_element.namespaceURI == "urn:schemas-microsoft-com:asm.v1"
        assert root_element.attributes["manifestVersion"].value == "1.0"

        # Modify the manifest
        _set_execution_level(manifest_dom, root_element, uac_admin, uac_uiaccess)
        _ensure_common_controls_dependency(manifest_dom, root_element)

        # Create output XML
        output = manifest_dom.toprettyxml(indent="  ", encoding="UTF-8")

    # Strip extra newlines
    output = [line for line in output.splitlines() if line.strip()]

    # Replace: `<?xml version="1.0" encoding="UTF-8"?>` with `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>`.
    # Support for `standalone` was added to `toprettyxml` in python 3.9, so do a manual work around.
    output[0] = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>"""

    output = b"\n".join(output)

    return output


def write_manifest_to_executable(filename, manifest_xml):
    """
    Write the given manifest XML to the given executable's RT_MANIFEST resource.
    """
    from PyInstaller.utils.win32 import winresource

    # CREATEPROCESS_MANIFEST_RESOURCE_ID is used for manifest resource in executables.
    # ISOLATIONAWARE_MANIFEST_RESOURCE_ID is used for manifest resources in DLLs.
    names = [CREATEPROCESS_MANIFEST_RESOURCE_ID]

    # Ensure LANG_NEUTRAL is updated, and also update any other present languages.
    languages = [LANG_NEUTRAL, "*"]

    winresource.add_or_update_resource(filename, manifest_xml, RT_MANIFEST, names, languages)


def read_manifest_from_executable(filename):
    """
    Read manifest from the given executable."
    """
    from PyInstaller.utils.win32 import winresource

    resources = winresource.get_resources(filename, [RT_MANIFEST])

    # `resources` is a three-level dictionary:
    #  - level 1: resource type (RT_MANIFEST)
    #  - level 2: resource name (CREATEPROCESS_MANIFEST_RESOURCE_ID)
    #  - level 3: resource language (LANG_NEUTRAL)

    # Level 1
    if RT_MANIFEST not in resources:
        raise ValueError(f"No RT_MANIFEST resources found in {filename!r}.")
    resources = resources[RT_MANIFEST]

    # Level 2
    if CREATEPROCESS_MANIFEST_RESOURCE_ID not in resources:
        raise ValueError(f"No RT_MANIFEST resource named CREATEPROCESS_MANIFEST_RESOURCE_ID found in {filename!r}.")
    resources = resources[CREATEPROCESS_MANIFEST_RESOURCE_ID]

    # Level 3
    # We prefer LANG_NEUTRAL, but allow fall back to the first available entry.
    if LANG_NEUTRAL in resources:
        resources = resources[LANG_NEUTRAL]
    else:
        resources = next(iter(resources.items()))

    manifest_xml = resources
    return manifest_xml
