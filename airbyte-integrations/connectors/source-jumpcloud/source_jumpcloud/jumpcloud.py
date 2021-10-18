from enum import Enum
from typing import Union
import jcapiv2
from jcapiv2.rest import ApiException

from jcapiv2 import (
    AppleMDMApi,
    ActiveDirectoryApi,
    DirectoriesApi,
    GroupsApi,
    LDAPServersApi,
    PoliciesApi,
    PolicytemplatesApi,
    SystemGroupsApi,
    UserGroupsApi,
    SystemInsightsApi,
    WorkdayImportApi
)

# Exceptions
class UnauthorizedAccess(Exception):
    pass

class UnknownException(Exception):
    pass

class ApiDoesntExist(Exception):
    pass

# Enums
class JumpcloudAPI(Enum):
    APPLE_MDM               = 1
    ACTIVE_DIRECTORIES      = 2
    DIRECTORIES             = 3
    GROUPS                  = 4
    LDAP_SERVERS            = 5
    POLICIES                = 6
    POLICY_TEMPLATES        = 7
    SYSTEM_GROUPS           = 8
    USER_GROUPS             = 9
    SYSTEM_INSIGHTS         = 10
    WORKDAY                 = 11

# Jumpcloud Object
class Jumpcloud:
    '''
    Jumpcloud Object is a custom adapter for JCAPIV2.
    '''

    def __init__(self, api_key : str, content_type : str = "application/json", accept : str = "application/json") -> None:
        '''
        Initializing all the parameters.
        '''
        self._API_KEY = api_key
        self.CONTENT_TYPE = content_type
        self.ACCEPT = accept

        self.CONFIGURATION = jcapiv2.Configuration()
        self.CONFIGURATION.api_key['x-api-key'] = self._API_KEY

        self.API_CLIENT = jcapiv2.ApiClient(self.CONFIGURATION)
        self.INSTANCES = {}
        
        # To check if the API KEY is valid
        try:
            jcapiv2.SystemGroupsApi(self.API_CLIENT).groups_system_list(self.CONTENT_TYPE, self.ACCEPT)
        except ApiException as apierr:
            if apierr.status == 401:
                raise UnauthorizedAccess("Unauthorized Access. Wrong API Key provided")
            else:
                raise UnknownException("Unknown Exception Occurred")

    def _convert_to_dict(self, records):
        '''
        Converts the list of SystemInsights* Object to list of dictionary
        '''
        return [record.to_dict() for record in records]

    def _get_all(self, api_function, to_dict : bool = False):
        '''
        Calls the callback function : `api_function` with `CONTENT_TYPE` and `ACCEPT` headers

        Fetches all the records available.
        '''
        try:
            records = []
            i = 1
            limit = 100
            
            temp_records = api_function(
                                        self.CONTENT_TYPE, 
                                        self.ACCEPT, 
                                        limit = limit,
                                        )            
            records.extend(self._convert_to_dict(temp_records) if to_dict else temp_records)
            if len(temp_records) == limit:
                while len(temp_records) == limit:
                    temp_records = api_function(
                                                self.CONTENT_TYPE, 
                                                self.ACCEPT, 
                                                skip = i * limit, 
                                                limit = limit, 
                                            )
                    records.extend(self._convert_to_dict(temp_records) if to_dict else temp_records)

                    # print(f"Records read : {len(records)}")
                    i += 1

            return records

        except ApiException as err:
            print(f"Exception Occurred : {err}")

    def _get_instance(self, name : JumpcloudAPI) -> Union[
            AppleMDMApi,
            ActiveDirectoryApi,
            DirectoriesApi,
            GroupsApi,
            LDAPServersApi,
            PoliciesApi,
            PolicytemplatesApi,
            SystemGroupsApi,
            UserGroupsApi,
            SystemInsightsApi,
            WorkdayImportApi
        ]:
        '''
        Maintains a single instance of different API's
        '''
        if name not in self.INSTANCES.keys():
            # Add other API's here to maintain a single instance
            if name == JumpcloudAPI.APPLE_MDM:
                self.INSTANCES[name] = AppleMDMApi(self.API_CLIENT)

            elif name == JumpcloudAPI.ACTIVE_DIRECTORIES:
                self.INSTANCES[name] = ActiveDirectoryApi(self.API_CLIENT)

            elif name == JumpcloudAPI.DIRECTORIES:
                self.INSTANCES[name] = DirectoriesApi(self.API_CLIENT)

            elif name == JumpcloudAPI.GROUPS:
                self.INSTANCES[name] = GroupsApi(self.API_CLIENT)

            elif name == JumpcloudAPI.LDAP_SERVERS:
                self.INSTANCES[name] = LDAPServersApi(self.API_CLIENT)

            elif name == JumpcloudAPI.POLICIES:
                self.INSTANCES[name] = PoliciesApi(self.API_CLIENT)

            elif name == JumpcloudAPI.POLICY_TEMPLATES:
                self.INSTANCES[name] = PolicytemplatesApi(self.API_CLIENT)

            elif name == JumpcloudAPI.SYSTEM_GROUPS:
                self.INSTANCES[name] = SystemGroupsApi(self.API_CLIENT)

            elif name == JumpcloudAPI.USER_GROUPS:
                self.INSTANCES[name] = UserGroupsApi(self.API_CLIENT)

            elif name == JumpcloudAPI.SYSTEM_INSIGHTS:
                self.INSTANCES[name] = SystemInsightsApi(self.API_CLIENT)

            elif name == JumpcloudAPI.WORKDAY:
                self.INSTANCES[name] = WorkdayImportApi(self.API_CLIENT)

            else:
                raise ApiDoesntExist("Api Doesn't Exist")
        
        return self.INSTANCES[name]

    # --------------------- APPLE MDMs API -------------------------------------------

    def get_all_apple_mdms(self):
        api : AppleMDMApi = self._get_instance(JumpcloudAPI.APPLE_MDM)
        return self._convert_to_dict(api.applemdms_list(self.CONTENT_TYPE, self.ACCEPT))

    # --------------------- ACTIVE DIRECTORIES API -----------------------------------

    def get_all_active_directories(self):
        api : ActiveDirectoryApi = self._get_instance(JumpcloudAPI.ACTIVE_DIRECTORIES)
        return self._get_all(api.activedirectories_list, to_dict=True)

    # --------------------- DIRECTORIES API ------------------------------------------

    def get_all_directories(self):
        api : DirectoriesApi = self._get_instance(JumpcloudAPI.DIRECTORIES)
        return self._get_all(api.directories_list, to_dict=True)

    # --------------------- LDAP SERVERS API -----------------------------------------

    def get_all_ldap_servers(self):
        api : LDAPServersApi = self._get_instance(JumpcloudAPI.LDAP_SERVERS)
        return self._get_all(api.ldapservers_list, to_dict=True)

    # --------------------- POLICIES API ---------------------------------------------

    def get_all_policies(self):
        api : PoliciesApi = self._get_instance(JumpcloudAPI.POLICIES)
        return self._get_all(api.policies_list, to_dict=True)

    def get_all_policy_results(self):
        api : PoliciesApi = self._get_instance(JumpcloudAPI.POLICIES)
        return self._get_all(api.policyresults_org_list, to_dict=True)

    def get_all_policy_templates(self):
        api : PolicytemplatesApi = self._get_instance(JumpcloudAPI.POLICY_TEMPLATES)
        return self._get_all(api.policytemplates_list, to_dict=True)

    # --------------------- SYSTEM GROUPS API ----------------------------------------

    def get_all_system_groups(self):
        api : SystemGroupsApi = self._get_instance(JumpcloudAPI.SYSTEM_GROUPS)
        return self._get_all(api.groups_system_list, to_dict=True)

    # --------------------- USER GROUPS API -----------------------------------------

    def get_all_user_groups(self):
        api : UserGroupsApi = self._get_instance(JumpcloudAPI.USER_GROUPS)
        return self._get_all(api.groups_user_list, to_dict=True)

    # --------------------- SYSTEM INSIGHTS API --------------------------------------

    def get_all_system_insights_apps(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_apps, to_dict=True)

    def get_all_system_insights_battery(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_battery, to_dict=True)

    def get_all_system_insights_bitlocker_info(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_bitlocker_info, to_dict=True)

    def get_all_system_insights_browser_plugins(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_browser_plugins, to_dict=True)

    def get_all_system_insights_chrome_extensions(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_chrome_extensions, to_dict=True)

    # Doesn't give system_id attribute?????
    def get_all_system_insights_crashes(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_crashes, to_dict=True)

    def get_all_system_insights_disk_encryption(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_disk_encryption, to_dict=True)

    def get_all_system_insights_disk_info(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_disk_info, to_dict=True)

    def get_all_system_insights_etc_hosts(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_etc_hosts, to_dict=True)

    def get_all_system_insights_firefox_addons(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_firefox_addons, to_dict=True)

    def get_all_system_insights_groups(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_groups, to_dict=True)

    def get_all_system_insights_ie_extensions(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_ie_extensions, to_dict=True)

    def get_all_system_insights_interface_addresses(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_interface_addresses, to_dict=True)

    def get_all_system_insights_kernel_info(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_kernel_info, to_dict=True)

    def get_all_system_insights_launchd(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_launchd, to_dict=True)

    def get_all_system_insights_logged_in_users(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_logged_in_users, to_dict=True)
        
    def get_all_system_insights_logical_drives(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_logical_drives, to_dict=True)

    def get_all_system_insights_mounts(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_mounts, to_dict=True)

    def get_all_system_insights_os_version(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_os_version, to_dict=True)
        
    def get_all_system_insights_patches(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_patches, to_dict=True)
        
    def get_all_system_insights_programs(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_programs, to_dict=True)
        
    def get_all_system_insights_safari_extensions(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_safari_extensions, to_dict=True)
        
    def get_all_system_insights_uptime(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_uptime, to_dict=True)
        
    def get_all_system_insights_usb_devices(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_usb_devices, to_dict=True)
        
    def get_all_system_insights_user_groups(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_user_groups, to_dict=True)
        
    def get_all_system_insights_users(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_users, to_dict=True)

    # Takes longer time
    def get_all_system_insights_system_controls(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_system_controls, to_dict=True)

    def get_all_system_insights_system_info(self):
        api : SystemInsightsApi = self._get_instance(JumpcloudAPI.SYSTEM_INSIGHTS)
        return self._get_all(api.systeminsights_list_system_info, to_dict=True)