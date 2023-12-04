INSTANCES_SCHEMA: dict = {
    "type": ["null", "object"],
    "properties": {
        "approval_code": {
            "type": ["null", "string"]
        },
        "approval_name": {
            "type": ["null", "string"]
        },
        "department_id": {
            "type": ["null", "string"]
        },
        "end_time": {
            "type": ["null", "string"]
        },
        "form": {
            "type": ["null", "string"]
        },
        "instance_code": {
            "type": ["null", "string"]
        },
        "open_id": {
            "type": ["null", "string"]
        },
        "reverted": {
            "type": ["null", "string"]
        },
        "serial_number": {
            "type": ["null", "string"]
        },
        "start_time": {
            "type": ["null", "string"]
        },
        "status": {
            "type": ["null", "string"]
        },
        "task_list": {
            "type": ["null", "array"]
        },
        "timeline": {
            "type": ["null", "array"]
        },
        "user_id": {
            "type": ["null", "string"]
        },
        "uuid": {
            "type": ["null", "string"]
        }
    }
}

SCHEMA_HEADERS: dict = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

VIEW_LIST_SCHEMA: dict = {
  "type": ["null", "object"],
  "properties": {
    "app_token": {
      "type": ["null", "string"]
    },
    "table_id": {
      "type": ["null", "string"]
    },
    "view_id": {
      "type": ["null", "string"]
    },
    "view_name": {
      "type": ["null", "string"]
    },
    "view_public_level": {
      "type": ["null", "string"]
    },
    "view_type": {
      "type": ["null", "string"]
    }
  }
}

TABLE_LIST_SCHEMA: dict = {
  "type": ["null", "object"],
  "properties": {
    "app_token": {
      "type": ["null", "string"]
    },
    "table_id": {
      "type": ["null", "string"]
    },
    "revision": {
      "type": ["null", "string"]
    },
    "name": {
      "type": ["null", "string"]
    }
  }
}

ROLE_LIST_SCHEMA: dict = {
  "type": ["null", "object"],
  "properties": {
    "app_token": {
      "type": ["null", "string"]
    },
    "role_id": {
      "type": ["null", "string"]
    },
    "role_name": {
      "type": ["null", "string"]
    },
    "table_roles": {
      "type": ["null", "array"]
    },
    "block_roles": {
      "type": ["null", "array"]
    }
  }
}

RECORD_LIST_SCHEMA: dict = {
  "type": ["null", "object"],
  "properties": {
    "app_token": {
      "type": ["null", "string"]
    },
    "table_id": {
      "type": ["null", "string"]
    },
    "record_id": {
      "type": ["null", "string"]
    },
    "id": {
      "type": ["null", "string"]
    },
    "fields": {
      "type": ["null", "string"]
    }
  }
}

MEMBER_LIST_SCHEMA: dict = {
  "type": ["null", "object"],
  "properties": {
    "app_token": {
      "type": ["null", "string"]
    },
    "member_type": {
      "type": ["null", "string"]
    },
    "member_open_id": {
      "type": ["null", "string"]
    },
    "member_user_id": {
      "type": ["null", "string"]
    },
    "perm": {
      "type": ["null", "string"]
    }
  }
}

FIELD_LIST_SCHEMA: dict = {
  "type": ["null", "object"],
  "properties": {
    "app_token": {
      "type": ["null", "string"]
    },
    "table_id": {
      "type": ["null", "string"]
    },
    "field_id": {
      "type": ["null", "string"]
    },
    "field_name": {
      "type": ["null", "string"]
    },
    "is_primary": {
      "type": ["null", "string"]
    },
    "property": {
      "type": ["null", "string"]
    },
    "type": {
      "type": ["null", "string"]
    },
    "ui_type": {
      "type": ["null", "string"]
    }
  }
}

DASHBOARD_LIST_SCHEMA: dict = {
  "type": ["null", "object"],
  "properties": {
    "app_token": {
      "type": ["null", "string"]
    },
    "block_id": {
      "type": ["null", "string"]
    },
    "name": {
      "type": ["null", "string"]
    }
  }
}
