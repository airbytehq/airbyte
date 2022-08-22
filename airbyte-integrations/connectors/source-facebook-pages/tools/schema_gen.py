#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

"""
Docs: https://developers.facebook.com/docs/graph-api/reference/page

List of all Facebook nodes: https://github.com/facebook/facebook-business-sdk-codegen

Schemas for required streams:
Page: facebook-business-sdk-codegen/api_specs/specs/Page.json
Post: facebook-business-sdk-codegen/api_specs/specs/Post.json

FB schema contains the following attrs:
- fields:
    - with default types:
        - ['string', 'integer', 'boolean', 'array']
        - default is 'string' (for map<...> )
    - with <FB_node> type:
        '<FB_NODE>'
    - with list of <FB_node> type:
        'list<FB_NODE>'
- edges:
     {
         "method": "GET",
         "endpoint": "indexed_videos",   <-- field name
         "return": "AdVideo",            <-- field FB_NODE
         "params": []
     }

Mapping rules:
- all 'default' types are mapped to 'default' json schema types
- all FB_NODE types are converted as a reference to separate 'shared/<FB_NODE>.json', for example:
    FROM:
        {
            "name": "connected_instagram_account",
            "type": "IGUser"
        },
    TO:
        "connected_instagram_account": {
          "$ref": "iguser.json"
        }
- schemas for all referenced sub nodes contains 'default' types ONLY (no references to sub nodes).

                                      MAPPING EXAMPLE

FACEBOOK schema:                            VS                  AIRBYTE schema:
{                                                               {
    "fields": [                                                     "about": {
        {                                                              "type": ["string", "null"]
            "name": "about",                                        },
            "type": "string"                                        "emails": {
        },                                                              "type": ["array", "null"]
        {                                                               "items": {
            "name": "emails",                                               "type": ["string", "null"]
            "type": "list<string>"                                      }
        },                                                          },
        {                                                           "hours": {
            "name": "hours",                                            "type": ["string", "null"]
            "type": "map<string, string>"                           },
        },                                                          "connected_instagram_account": {
        {                                                               "$ref": "iguser.json"
            "name": "connected_instagram_account",                  },
            "type": "IGUser"                                        "category_list": {
        },                                                              "type": ["array", "null"]
        {                                                               "items": {
            "name": "category_list",                                        "$ref": "pagecategory.json"
            "type": "list<PageCategory>"                                }
        },                                                          },
                                                                    "ads_posts": {
    ],                                                                  "type": [ "object", "null"],
    "apis": [                                                           "properties": {
        {                                                                   "data": {
            "method": "GET",                                                    "type": ["array", "null"],
            "endpoint": "ads_posts",                                            "items": {
            "return": "PagePost",                                                   "$ref": "pagepost.json"
            "params": [                                                         }
                { .... }                                                    },
            ]                                                               "paging": {
        }                                                                       "type": ["object", "null"],
    ]                                                                           "properties": {
}                                                                                   "previous": {
                                                                                        "type": ["string", "null"]
                                                                                    },
                                                                                    "next": {
                                                                                        "type": ["string", "null"]
                                                                                    },
                                                                                    "cursors": {
                                                                                        "type": "object",
                                                                                        "properties": {
                                                                                            "before": {
                                                                                                "type": ["string", "null"]
                                                                                            },
                                                                                            "after": {
                                                                                                "type": ["string", "null"]
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }

"""

import json
import os

spec_path = "facebook-business-sdk-codegen/api_specs/specs"
fb_node_files = os.listdir(spec_path)
fb_node_files.sort()
FB_NODES = [name.split(".")[0] for name in fb_node_files]

print(f"FB SDK identifies specs for {len(FB_NODES)} nodes in ./{spec_path}")

FB_TYPE_DEFAULT = {"type": ["string", "null"]}

FB_TYPES = {
    "int": {"type": ["integer", "null"]},
    "int32": {"type": ["integer", "null"]},
    "unsigned int32": {"type": ["integer", "null"]},
    "unsigned int": {"type": ["integer", "null"]},
    "float": {"type": ["number", "null"]},
    "string": {"type": ["string", "null"]},
    "numeric string": {"type": ["string", "null"]},
    "datetime": {"type": ["string", "null"], "format": "datetime"},
    "id": {"type": ["string", "null"]},
    "enum": {"type": ["string", "null"]},
    "bool": {"type": ["boolean", "null"]},
    "Object": {"type": ["string", "null"]},
    "list": {
        "type": ["array", "null"],
        "items": {
            "type": ["string", "null"],
        },
    },
    "list<string>": {
        "type": ["array", "null"],
        "items": {
            "type": ["string", "null"],
        },
    },
    "list<numeric string>": {
        "type": ["array", "null"],
        "items": {
            "type": ["string", "null"],
        },
    },
    "list<int>": {
        "type": ["array", "null"],
        "items": {
            "type": ["integer", "null"],
        },
    },
    "list<unsigned int>": {
        "type": ["array", "null"],
        "items": {
            "type": ["integer", "null"],
        },
    },
    "list<list<int>>": {
        "type": ["array", "null"],
        "items": {
            "type": ["array", "null"],
            "items": {
                "type": ["integer", "null"],
            },
        },
    },
    # 'map' is not supported because it is not possible to identify field names, which are required for destinations
    # so 'map' attr will be converted and saved as string
    # "map": {
    #   "type": ["object", "null"],
    #   "properties": {
    #     "id": {
    #       "type": ["string", "null"],
    #     }
    #   }
    # },
    # "map<string, unsigned int32>": {
    #   "type": ["object", "null"],
    #   "properties": {
    #     "id": {
    #       "type": ["integer", "null"],
    #     }
    #   }
    # },
    # "map<string, unsigned int>": {
    #   "type": ["object", "null"],
    #   "properties": {
    #     "id": {
    #       "type": ["integer", "null"],
    #     }
    #   }
    # },
    # "map<string, float>": {
    #   "type": ["object", "null"],
    #   "properties": {
    #     "id": {
    #       "type": ["integer", "null"],
    #     }
    #   }
    # },
    # "map<string, string>": {
    #   "type": ["null", "object"],
    #   "properties": {
    #     "id": {
    #       "type": ["string", "null"],
    #     }
    #   }
    # },
    # "map<string, bool>": {
    #   "type": ["null", "object"],
    #   "properties": {
    #     "id": {
    #       "type": ["string", "boolean"],
    #     }
    #   }
    # }
}

# print(f'FB_TYPES: {len(FB_TYPES)} types')

#


def is_node(name):
    return name[0].isupper() and "_" not in name


def get_fields(fields, with_refs=False):

    # process Node's fields
    schema_fields = {}
    for attr in fields:
        is_list = False
        attr_name = attr["name"]
        fb_type = attr["type"]

        type_default = FB_TYPES.get(fb_type)

        # process attrs with default type
        if type_default:
            schema_fields[attr_name] = type_default
            continue

        # list<PageCategory>"
        if fb_type.startswith("list<"):
            is_list = True
            fb_type = fb_type.split("<")[1].strip(">")

        # process attrs with unknown type as string
        if not is_node(fb_type):
            if not is_list:
                schema_fields[attr_name] = FB_TYPE_DEFAULT
            else:
                # /home/vratniuk/air/sandbox/schema_gen_fb/facebook-business-sdk-codegen/api_specs/specs/AdSet.json
                # {
                #     "name": "bid_strategy",
                #     "type": "AdSet_bid_strategy"  <--- THIS IS ENUM
                # },
                schema_fields[attr_name] = {"type": ["array", "null"], "items": {"type": ["array", "null"], "items": FB_TYPE_DEFAULT}}
            print(f"    use 'string' type for UNSUPPORTED attr type '{fb_type}' in field: {attr}")
            continue

        if not with_refs:
            continue

        # process attrs with Node type
        if fb_type in FB_NODES:
            FOUND_SUBNODES.add(fb_type)
            if not is_list:
                schema_fields[attr_name] = {"$ref": f"{fb_type.lower()}.json"}
            else:
                schema_fields[attr_name] = {"type": ["array", "null"], "items": {"$ref": f"{fb_type.lower()}.json"}}

        else:
            print(f"    skip UNKNOWN NODE type '{fb_type}' in field: {attr}")

    return schema_fields


def get_edges(edges):

    schema_edges = {}
    attrs = {}
    for attr in edges:
        if attr["method"] == "GET":
            # {
            #     "method": "GET",
            #     "endpoint": "indexed_videos",
            #     "return": "AdVideo",
            #     "params": []
            # },
            attr_name = attr.get("endpoint")
            attr_type = attr.get("return")
            if not attr_name:
                print(f"    skip UNSUPPORTED edge format: {attr}")
                continue
            if attr_type not in FB_NODES:
                print(f"    skip UNKNOWN NODE type '{attr_type}' in edge: {attr}")
                continue

            attrs[attr_name] = attr_type
            FOUND_SUBNODES.add(attr_type)

    for attr_name, attr_type in attrs.items():
        # https://developers.facebook.com/docs/graph-api/results
        schema_edges[attr_name] = {
            "type": ["object", "null"],
            "properties": {
                "data": {"type": ["array", "null"], "items": {"$ref": f"{attr_type.lower()}.json"}},
                "paging": {
                    "type": ["object", "null"],
                    "properties": {
                        "previous": {"type": ["string", "null"]},
                        "next": {"type": ["string", "null"]},
                        "cursors": {
                            "type": "object",
                            "properties": {"before": {"type": ["string", "null"]}, "after": {"type": ["string", "null"]}},
                        },
                    },
                },
            },
        }

    return schema_edges


def build_schema(node_name, with_refs=False):

    file_path = f"{spec_path}/{node_name}.json"
    print(f"Fetching schema from file: {file_path}")

    fb_node_sdk = json.load(open(file_path))

    # process Node's fields
    schema = get_fields(fb_node_sdk["fields"], with_refs=with_refs)

    if with_refs:
        # process Node's edges
        schema_edges = get_edges(fb_node_sdk["apis"])
        schema.update(schema_edges)

    return schema


# get schema for main Page and Post nodes
FOUND_SUBNODES = set()

MAIN_NODES = ["Page", "Post"]
print(f"Process main nodes: {MAIN_NODES}")

for node_name in MAIN_NODES:

    page_schema = build_schema(node_name=node_name, with_refs=True)

    SCHEMA = {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": page_schema}
    file_name = node_name.lower()
    json.dump(SCHEMA, open(f"./schemas/{file_name}.json", "w"), indent=2)

print(f"Process found : {len(FOUND_SUBNODES)} SUBNODES")


# get schema for all found subnodes

for node_name in FOUND_SUBNODES:
    file_name = node_name.lower()
    SCHEMA = {"type": ["object", "null"], "properties": build_schema(node_name=node_name)}
    json.dump(SCHEMA, open(f"./schemas/shared/{file_name}.json", "w"), indent=2)

#
print("DONE!")

""" OUTPUT EXAMPLE:

FB SDK identifies specs for 420 nodes in ./facebook-business-sdk-codegen/api_specs/specs
Process main nodes: ['Page', 'Post']
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Page.json
    use 'string' type for UNSUPPORTED attr type 'map<string, bool>' in field: {'name': 'differently_open_offerings', 'type': 'map<string, bool>'}
    use 'string' type for UNSUPPORTED attr type 'map<string, string>' in field: {'name': 'hours', 'type': 'map<string, string>'}
    skip UNKNOWN NODE type 'BusinessProject' in edge: {'method': 'GET', 'endpoint': 'businessprojects', 'return': 'BusinessProject', 'params': [{'name': 'business', 'required': False, 'type': 'string'}]}
    skip UNKNOWN NODE type 'PageInsightsAsyncExportRun' in edge: {'method': 'GET', 'endpoint': 'insights_exports', 'return': 'PageInsightsAsyncExportRun', 'params': [{'name': 'data_level', 'required': False, 'type': 'list<string>'}, {'name': 'from_creation_date', 'required': False, 'type': 'datetime'}]}
    skip UNSUPPORTED edge format: {'name': '#get', 'method': 'GET', 'return': 'Page', 'params': [{'name': 'account_linking_token', 'required': False, 'type': 'string'}]}
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Post.json
    skip UNKNOWN NODE type 'StoryAttachment' in edge: {'method': 'GET', 'endpoint': 'attachments', 'return': 'StoryAttachment', 'params': []}
    skip UNSUPPORTED edge format: {'name': '#get', 'method': 'GET', 'return': 'Post', 'params': []}
Process found : 70 SUBNODES
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/AssignedUser.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/CommerceOrder.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/PageRestaurantSpecialties.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/User.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/URL.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/AdSet.json
    use 'string' type for UNSUPPORTED attr type 'map<string, unsigned int>' in field: {'name': 'bid_info', 'type': 'map<string, unsigned int>'}
    use 'string' type for UNSUPPORTED attr type 'AdSet_bid_strategy' in field: {'name': 'bid_strategy', 'type': 'AdSet_bid_strategy'}
    use 'string' type for UNSUPPORTED attr type 'AdSet_billing_event' in field: {'name': 'billing_event', 'type': 'AdSet_billing_event'}
    use 'string' type for UNSUPPORTED attr type 'AdSet_configured_status' in field: {'name': 'configured_status', 'type': 'AdSet_configured_status'}
    use 'string' type for UNSUPPORTED attr type 'AdSet_effective_status' in field: {'name': 'effective_status', 'type': 'AdSet_effective_status'}
    use 'string' type for UNSUPPORTED attr type 'AdSet_optimization_goal' in field: {'name': 'optimization_goal', 'type': 'AdSet_optimization_goal'}
    use 'string' type for UNSUPPORTED attr type 'AdSet_status' in field: {'name': 'status', 'type': 'AdSet_status'}
    use 'string' type for UNSUPPORTED attr type 'map<string, int>' in field: {'name': 'targeting_optimization_types', 'type': 'map<string, int>'}
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Shop.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/PagePost.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/CommerceMerchantSettings.json
    use 'string' type for UNSUPPORTED attr type 'map<string, string>' in field: {'name': 'privacy_url_by_locale', 'type': 'map<string, string>'}
    use 'string' type for UNSUPPORTED attr type 'map<string, string>' in field: {'name': 'terms_url_by_locale', 'type': 'map<string, string>'}
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/MessagingFeatureReview.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Engagement.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/CoverPhoto.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Profile.json
    use 'string' type for UNSUPPORTED attr type 'Profile_profile_type' in field: {'name': 'profile_type', 'type': 'Profile_profile_type'}
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/RTBDynamicPost.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/VideoList.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/CommercePayout.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/MessagingFeatureStatus.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Post.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Photo.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Location.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/PagePaymentOptions.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/PageParking.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/ProductCatalog.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/CommerceOrderTransactionDetail.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/PageCommerceEligibility.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/CanvasBodyElement.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/CommerceMerchantSettingsSetupStatus.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/UnifiedThread.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/InsightsResult.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Application.json
    use 'string' type for UNSUPPORTED attr type 'map' in field: {'name': 'client_config', 'type': 'map'}
    use 'string' type for UNSUPPORTED attr type 'map<string, bool>' in field: {'name': 'migrations', 'type': 'map<string, bool>'}
    use 'string' type for UNSUPPORTED attr type 'Application_supported_platforms' in field: {'name': 'supported_platforms', 'type': 'list<Application_supported_platforms>'}
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/PageCategory.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/ProfilePictureSource.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/InstantArticle.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/MediaFingerprint.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/NativeOffer.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Recommendation.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Event.json
    use 'string' type for UNSUPPORTED attr type 'Event_category' in field: {'name': 'category', 'type': 'Event_category'}
    use 'string' type for UNSUPPORTED attr type 'Event_online_event_format' in field: {'name': 'online_event_format', 'type': 'Event_online_event_format'}
    use 'string' type for UNSUPPORTED attr type 'Event_type' in field: {'name': 'type', 'type': 'Event_type'}
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/InstagramUser.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Targeting.json
    use 'string' type for UNSUPPORTED attr type 'Targeting_device_platforms' in field: {'name': 'device_platforms', 'type': 'list<Targeting_device_platforms>'}
    use 'string' type for UNSUPPORTED attr type 'Targeting_effective_device_platforms' in field: {'name': 'effective_device_platforms', 'type': 'list<Targeting_effective_device_platforms>'}
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/PageSettings.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/MailingAddress.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/ImageCopyright.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/InstantArticleInsightsQueryResult.json
    use 'string' type for UNSUPPORTED attr type 'map<string, string>' in field: {'name': 'breakdowns', 'type': 'map<string, string>'}
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Privacy.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/VideoCopyrightRule.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Place.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Page.json
    use 'string' type for UNSUPPORTED attr type 'map<string, bool>' in field: {'name': 'differently_open_offerings', 'type': 'map<string, bool>'}
    use 'string' type for UNSUPPORTED attr type 'map<string, string>' in field: {'name': 'hours', 'type': 'map<string, string>'}
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/IGUser.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/VoipInfo.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/PageStartInfo.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Album.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/LiveVideo.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/AdVideo.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Persona.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/PageThreadOwner.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Comment.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/CustomUserSettings.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/PageAdminNote.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/PageCallToAction.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/LeadgenForm.json
    use 'string' type for UNSUPPORTED attr type 'map<string, string>' in field: {'name': 'tracking_parameters', 'type': 'map<string, string>'}
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/MessengerProfile.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/PageUserMessageThreadLabel.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Group.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Canvas.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Tab.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/Business.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/PageRestaurantServices.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/MessengerDestinationPageWelcomeMessage.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/ChatPlugin.json
Fetching schema from file: facebook-business-sdk-codegen/api_specs/specs/LiveEncoder.json
DONE!
"""
