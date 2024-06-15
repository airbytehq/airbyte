# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

children_record = {
    "children": {
          "data": [
            {
              "id": "7608776690540"
            },
            {
              "id": "2896800415362"
            },
            {
              "id": "9559889460059"
            },
            {
              "id": "7359925580923"
            }
          ]
        }
}

expected_children_transformed = {
    "children":
        [
          {
            "id": "7608776690540",
            "ig_id": "2521545917836833225",
            "media_type": "IMAGE",
            "media_url": "https://fake_url?_nc_cat=108&ccb=1-7&_nc_sid=18de74&_nc_ohc=tTUSyCXbN40Q7kNvgF-k3H6&_nc_ht=fakecontent&edm=AEQ6tj4EAAAA&oh=00_AYAe4PKmuen4Dryt4sMEbfvrW2_eANbY1AEdl7gHG0a3mw&oe=66701C8F",
            "owner": {
              "id": "id"
            },
            "shortcode": "shortcode",
            "timestamp": "2021-03-03T22:48:39+00:00",
            "username": "username"
          },
          {
            "id": "2896800415362",
            "ig_id": "2521545917736276706",
            "media_type": "IMAGE",
            "media_url": "https://fake_url?_nc_cat=100&ccb=1-7&_nc_sid=18de74&_nc_ohc=9qJ5-fOc9lcQ7kNvgFirW6U&_nc_ht=fakecontent&edm=AEQ6tj4EAAAA&oh=00_AYBSuGRqMEzjxHri30L5NDs0irt7_7h-arKTYS8inrL56g&oe=66702E9A",
            "owner": {
              "id": "id"
            },
            "shortcode": "shortcode",
            "timestamp": "2021-03-03T22:48:39+00:00",
            "username": "username"
          },
          {
            "id": "9559889460059",
            "ig_id": "2521545917845406325",
            "media_type": "IMAGE",
            "media_url": "https://fake_url?_nc_cat=110&ccb=1-7&_nc_sid=18de74&_nc_ohc=QOtZzdxFjusQ7kNvgEqsuc2&_nc_ht=fakecontent&edm=AEQ6tj4EAAAA&oh=00_AYBPBGVS3NYW-h8oLwam_rWub-mE-9MLGc1EDVHtLJ2DBQ&oe=66702DE1",
            "owner": {
              "id": "id"
            },
            "shortcode": "shortcode",
            "timestamp": "2021-03-03T22:48:39+00:00",
            "username": "username"
          },
          {
            "id": "7359925580923",
            "ig_id": "2521545555591565193",
            "media_type": "VIDEO",
            "media_url": "https://fake_url?efg=eyJ2ZW5jb2RlX3RhZyI6InZ0c192b2RfdXJsZ2VuLmNhcm91c2VsX2l0ZW0udW5rbm93bi1DMy40ODAuZGFzaF9iYXNlbGluZV8xX3YxIn0&_nc_ht=fakecontent&_nc_cat=108&vs=863753484982045_2117350142",
            "owner": {
              "id": "id"
            },
            "shortcode": "shortcode",
            "thumbnail_url": "https://fake_url?_nc_cat=108&ccb=1-7&_nc_sid=18de74&_nc_ohc=pJkRskDC80UQ7kNvgFn3i4H&_nc_ht=fakecontent&edm=AEQ6tj4EAAAA&oh=00_AYBKK27CU9dvjiqPi9a4JKUIICp26HZ074-vgz0OVKFkbw&oe=66702104",
            "timestamp": "2021-03-03T22:48:39+00:00",
            "username": "username"
          }
        ]
}

clear_url_record = {
    "media_url": "https://fake_url?_nc_cat=100&ccb=1-7&_nc_sid=18de74&_nc_rid=testing",
    "profile_picture_url": "https://fake_url/fake.jpg?_nc_cat=111&_nc_sid=7d201b&ccb=testing",
}

clear_url_record_transformed = {
    "media_url": "https://fake_url?_nc_cat=100&ccb=1-7&_nc_sid=18de74",
    "profile_picture_url": "https://fake_url/fake.jpg?_nc_cat=111&_nc_sid=7d201b",
}
