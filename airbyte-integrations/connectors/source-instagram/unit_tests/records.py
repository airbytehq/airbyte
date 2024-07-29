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

breakdowns_record = {
        "name": "follower_demographics",
        "period": "lifetime",
        "title": "Follower demographics",
        "description": "The demographic characteristics of followers, including countries, cities and gender distribution.",
        "total_value": {
          "breakdowns": [
            {
              "dimension_keys": [
                "city"
              ],
              "results": [
                {
                  "dimension_values": [
                    "London, England"
                  ],
                  "value": 263
                },
                {
                  "dimension_values": [
                    "Sydney, New South Wales"
                  ],
                  "value": 467
                },
                {
                  "dimension_values": [
                    "Algiers, Algiers Province"
                  ],
                  "value": 58
                },
                {
                  "dimension_values": [
                    "Casablanca, Grand Casablanca"
                  ],
                  "value": 71
                },
                {
                  "dimension_values": [
                    "São Paulo, São Paulo (state)"
                  ],
                  "value": 139
                },
                {
                  "dimension_values": [
                    "Rio de Janeiro, Rio de Janeiro (state)"
                  ],
                  "value": 44
                },
                {
                  "dimension_values": [
                    "Perth, Western Australia"
                  ],
                  "value": 180
                },
                {
                  "dimension_values": [
                    "Berlin, Berlin"
                  ],
                  "value": 47
                },
                {
                  "dimension_values": [
                    "Kolkata, West Bengal"
                  ],
                  "value": 85
                },
                {
                  "dimension_values": [
                    "Phoenix, Arizona"
                  ],
                  "value": 39
                },
                {
                  "dimension_values": [
                    "Lagos, Lagos State"
                  ],
                  "value": 40
                },
                {
                  "dimension_values": [
                    "Dublin, Dublin"
                  ],
                  "value": 65
                },
                {
                  "dimension_values": [
                    "Pune, Maharashtra"
                  ],
                  "value": 72
                },
                {
                  "dimension_values": [
                    "Wollongong, New South Wales"
                  ],
                  "value": 43
                },
                {
                  "dimension_values": [
                    "Christchurch, Canterbury"
                  ],
                  "value": 42
                },
                {
                  "dimension_values": [
                    "Jakarta, Jakarta"
                  ],
                  "value": 46
                },
                {
                  "dimension_values": [
                    "Pretoria, Gauteng"
                  ],
                  "value": 54
                },
                {
                  "dimension_values": [
                    "Buenos Aires, Ciudad Autónoma de Buenos Aires"
                  ],
                  "value": 41
                },
                {
                  "dimension_values": [
                    "Gold Coast, Queensland"
                  ],
                  "value": 98
                },
                {
                  "dimension_values": [
                    "Sunshine Coast, Queensland"
                  ],
                  "value": 37
                },
                {
                  "dimension_values": [
                    "Melbourne, Victoria"
                  ],
                  "value": 338
                },
                {
                  "dimension_values": [
                    "Gurugram, Haryana"
                  ],
                  "value": 52
                },
                {
                  "dimension_values": [
                    "Delhi, Delhi"
                  ],
                  "value": 194
                },
                {
                  "dimension_values": [
                    "Los Angeles, California"
                  ],
                  "value": 66
                },
                {
                  "dimension_values": [
                    "Madrid, Comunidad de Madrid"
                  ],
                  "value": 65
                },
                {
                  "dimension_values": [
                    "Lahore, Punjab"
                  ],
                  "value": 41
                },
                {
                  "dimension_values": [
                    "Brisbane, Queensland"
                  ],
                  "value": 160
                },
                {
                  "dimension_values": [
                    "Adelaide, South Australia"
                  ],
                  "value": 93
                },
                {
                  "dimension_values": [
                    "Canberra, Australian Capital Territory"
                  ],
                  "value": 45
                },
                {
                  "dimension_values": [
                    "Lima, Lima Region"
                  ],
                  "value": 43
                },
                {
                  "dimension_values": [
                    "Istanbul, Istanbul Province"
                  ],
                  "value": 57
                },
                {
                  "dimension_values": [
                    "Toronto, Ontario"
                  ],
                  "value": 40
                },
                {
                  "dimension_values": [
                    "Chennai, Tamil Nadu"
                  ],
                  "value": 82
                },
                {
                  "dimension_values": [
                    "Mexico City, Distrito Federal"
                  ],
                  "value": 66
                },
                {
                  "dimension_values": [
                    "Auckland, Auckland Region"
                  ],
                  "value": 98
                },
                {
                  "dimension_values": [
                    "Cape Town, Western Cape"
                  ],
                  "value": 172
                },
                {
                  "dimension_values": [
                    "New York, New York"
                  ],
                  "value": 139
                },
                {
                  "dimension_values": [
                    "Cairo, Cairo Governorate"
                  ],
                  "value": 45
                },
                {
                  "dimension_values": [
                    "Dubai, Dubai"
                  ],
                  "value": 57
                },
                {
                  "dimension_values": [
                    "Santiago, Santiago Metropolitan Region"
                  ],
                  "value": 73
                },
                {
                  "dimension_values": [
                    "Mumbai, Maharashtra"
                  ],
                  "value": 195
                },
                {
                  "dimension_values": [
                    "Bangalore, Karnataka"
                  ],
                  "value": 195
                },
                {
                  "dimension_values": [
                    "Nairobi, Nairobi"
                  ],
                  "value": 50
                },
                {
                  "dimension_values": [
                    "Johannesburg, Gauteng"
                  ],
                  "value": 50
                },
                {
                  "dimension_values": [
                    "Hyderabad, Telangana"
                  ],
                  "value": 49
                }
              ]
            }
          ]
        },
        "id": "17841457631192237/insights/follower_demographics/lifetime"
      }

expected_breakdown_record_transformed = {
    "name": "follower_demographics",
    "period": "lifetime",
    "title": "Follower demographics",
    "description": "The demographic characteristics of followers, including countries, cities and gender distribution.",
    "value": {
      "London, England": 263,
      "Sydney, New South Wales": 467,
      "Algiers, Algiers Province": 58,
      "Casablanca, Grand Casablanca": 71,
      "São Paulo, São Paulo (state)": 139,
      "Rio de Janeiro, Rio de Janeiro (state)": 44,
      "Perth, Western Australia": 180,
      "Berlin, Berlin": 47,
      "Kolkata, West Bengal": 85,
      "Phoenix, Arizona": 39,
      "Lagos, Lagos State": 40,
      "Dublin, Dublin": 65,
      "Pune, Maharashtra": 72,
      "Wollongong, New South Wales": 43,
      "Christchurch, Canterbury": 42,
      "Jakarta, Jakarta": 46,
      "Pretoria, Gauteng": 54,
      "Buenos Aires, Ciudad Autónoma de Buenos Aires": 41,
      "Gold Coast, Queensland": 98,
      "Sunshine Coast, Queensland": 37,
      "Melbourne, Victoria": 338,
      "Gurugram, Haryana": 52,
      "Delhi, Delhi": 194,
      "Los Angeles, California": 66,
      "Madrid, Comunidad de Madrid": 65,
      "Lahore, Punjab": 41,
      "Brisbane, Queensland": 160,
      "Adelaide, South Australia": 93,
      "Canberra, Australian Capital Territory": 45,
      "Lima, Lima Region": 43,
      "Istanbul, Istanbul Province": 57,
      "Toronto, Ontario": 40,
      "Chennai, Tamil Nadu": 82,
      "Mexico City, Distrito Federal": 66,
      "Auckland, Auckland Region": 98,
      "Cape Town, Western Cape": 172,
      "New York, New York": 139,
      "Cairo, Cairo Governorate": 45,
      "Dubai, Dubai": 57,
      "Santiago, Santiago Metropolitan Region": 73,
      "Mumbai, Maharashtra": 195,
      "Bangalore, Karnataka": 195,
      "Nairobi, Nairobi": 50,
      "Johannesburg, Gauteng": 50,
      "Hyderabad, Telangana": 49
    },
    "id": "17841457631192237/insights/follower_demographics/lifetime"
  }

insights_record = {
    "data": [
      {
        "name": "comments",
        "period": "lifetime",
        "values": [
          {
            "value": 7
          }
        ],
        "title": "title1",
        "description": "Description1.",
        "id": "insta_id/insights/comments/lifetime"
      },
      {
        "name": "ig_reels_avg_watch_time",
        "period": "lifetime",
        "values": [
          {
            "value": 11900
          }
        ],
        "title": "2",
        "description": "Description2.",
        "id": "insta_id/insights/ig_reels_avg_watch_time/lifetime"
      },
      {
        "name": "ig_reels_video_view_total_time",
        "period": "lifetime",
        "values": [
          {
            "value": 25979677
          }
        ],
        "title": "title3",
        "description": "Description3.",
        "id": "insta_id/insights/ig_reels_video_view_total_time/lifetime"
      },
      {
        "name": "likes",
        "period": "lifetime",
        "values": [
          {
            "value": 102
          }
        ],
        "title": "title4",
        "description": "Description4.",
        "id": "insta_id/insights/likes/lifetime"
      },
      {
        "name": "plays",
        "period": "lifetime",
        "values": [
          {
            "value": 2176
          }
        ],
        "title": "title5",
        "description": "Description5.",
        "id": "insta_id/insights/plays/lifetime"
      },
      {
        "name": "reach",
        "period": "lifetime",
        "values": [
          {
            "value": 1842
          }
        ],
        "title": "title6",
        "description": "Description6.",
        "id": "insta_id/insights/reach/lifetime"
      },
      {
        "name": "saved",
        "period": "lifetime",
        "values": [
          {
            "value": 7
          }
        ],
        "title": "title7",
        "description": "Description7.",
        "id": "insta_id/insights/saved/lifetime"
      },
      {
        "name": "shares",
        "period": "lifetime",
        "values": [
          {
            "value": 1
          }
        ],
        "title": "title8",
        "description": "Description8.",
        "id": "insta_id/insights/shares/lifetime"
      }
    ]
}

insights_record_transformed = {
    "comments": 7,
    "ig_reels_avg_watch_time": 11900,
    "ig_reels_video_view_total_time": 25979677,
    "likes": 102,
    "plays": 2176,
    "reach": 1842,
    "saved": 7,
    "shares": 1,
}
