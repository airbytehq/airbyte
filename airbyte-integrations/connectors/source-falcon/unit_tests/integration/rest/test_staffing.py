# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unit_tests.integration.rest.test_base import TestBase


class TestStaffing(TestBase):
    space = "staffing"

class TestWorkersStaffingInfo(TestStaffing):
    stream_name = "workers_staffing_info"
    path = "workers"

class TestJobsStaffingInfo(TestStaffing):
    stream_name = "jobs_staffing_info"
    path = "jobs"

class TestJobFamiliesStaffingInfo(TestStaffing):
    stream_name = "job_families_staffing_info"
    path = "jobFamilies"

class TestJobProfilesStaffingInfo(TestStaffing):
    stream_name = "job_profiles_staffing_info"
    path = "jobProfiles"
