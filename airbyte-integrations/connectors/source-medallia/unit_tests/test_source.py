#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_medallia.authenticator import MedalliaOauth2Authenticator
from source_medallia.source import Feedback, Fields, initialize_authenticator


class TestAuthentication:
    def test_init_oauth2_authentication_init(self, oauth_config):
        oauth_authentication_instance = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_authentication_instance, MedalliaOauth2Authenticator)

    def test_init_oauth2_authentication_wrong_oauth_config_bad_auth_type(self, wrong_oauth_config_bad_auth_type):
        try:
            initialize_authenticator(config=wrong_oauth_config_bad_auth_type)
        except Exception as e:
            assert e.args[0] == "Config validation error. `auth_type` not specified."


class TestGraphQlQueries:
    def test_fields_request_body_json(self, config):
        stream = Fields(**config)
        query_json = stream.request_body_json(stream_state={}, stream_slice={})
        query = """
                query
                {
                    fields(first: 100, after: null) {
                    nodes
                {
                    id
                name
                description
                dataType
                multivalued
                filterable
                __typename
                ...on
                Field
                {
                    __typename
                    ...on
                EnumField
                {
                    options
                {
                    id
                name
                numericValue
                }
                }
                }
                }
                pageInfo
                {
                    hasNextPage
                endCursor
                }
                }
                }
        """
        assert [c for c in query_json['query'] if c.isalpha()] == [c for c in query if c.isalpha()]

    def test_feedback_request_body_json(self, config):
        stream = Feedback(**config)
        query_json = stream.request_body_json(stream_state={}, stream_slice={})
        query = """
                query {
                  feedback(first: 250, orderBy: [{direction: ASC, fieldId: "a_initial_finish_timestamp"}], filter: {fieldIds: ["a_initial_finish_timestamp"], gt: "0"}) {
                    nodes {
                      id
                      metaData: fieldDataList(filterUnanswered: true, fieldIds: []) {
                        field {
                          id
                          name
                        }
                        __typename
                        ...extendFieldData
                      }
                      questionData: fieldDataList(filterUnanswered: true, fieldIds: []) {
                        field {
                          id
                          name
                        }
                        __typename
                        ...extendFieldData
                      }
                    }
                    pageInfo {
                      hasNextPage
                      endCursor
                    }
                  }
                }
                fragment extendFieldData on FieldData {
                  __typename
                  ... on EnumFieldData {
                    options {
                      id
                      name
                      numericValue
                    }
                  }
                  ... on StringFieldData {
                    values
                  }
                  ... on CommentFieldData {
                    topics: ruleTopicTaggingsPage {
                      nodes {
                        topic {
                          id
                          name
                          hasDescendants
                          ancestors
                        }
                        persona
                        regions {
                          startIndex
                          endIndex
                        }
                      }
                    }
                    themes: dataTopicTaggingsPage {
                      nodes {
                        topic {
                          id
                          name
                        }
                        persona
                        regions {
                          startIndex
                          endIndex
                        }
                      }
                    }
                    sentiment: sentimentTaggingsPage {
                      nodes {
                        sentiment
                        persona
                        regions {
                          startIndex
                          endIndex
                        }
                      }
                    }
                  }
                  ... on IntFieldData {
                    values
                  }
                  ... on DateFieldData {
                    values
                  }
                  ... on UnitFieldData {
                    units {
                      id
                    }
                  }
                }
        """
        print(query_json['query'])
        assert [c for c in query_json['query'] if c.isalpha()] == [c for c in query if c.isalpha()]
