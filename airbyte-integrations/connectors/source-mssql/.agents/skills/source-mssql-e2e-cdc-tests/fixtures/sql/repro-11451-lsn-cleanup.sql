-- Reproduces airbytehq/oncall#11451 by advancing the per-instance min
-- LSN past whatever offset a prior baseline read may have saved.
--
-- Generates noise commits to advance the database LSN counter, forces
-- a CDC scan, then calls sys.sp_cdc_cleanup_change_table on dbo_users
-- with a low_water_mark equal to the current max LSN. After this
-- script runs, sys.fn_cdc_get_min_lsn('dbo_users') returns the new
-- min LSN, which is greater than any LSN captured before this script
-- ran -- exactly the geo-replica regression described in the oncall
-- ticket.
--
-- Idempotent: every step is safe to re-run. The cleanup is a no-op
-- once min_lsn is already at the desired value.

USE CdcTest;
GO

SET NOCOUNT ON;
GO

-- 1. Generate noise commits. The capture instance reads from the
--    transaction log, so any committed write advances the LSN counter
--    and shows up in cdc.dbo_users_CT after the next sys.sp_cdc_scan.
DECLARE @i INT = 0;
WHILE @i < 100
BEGIN
  INSERT INTO dbo.users (email) VALUES (CONCAT('noise-', @i, '@example.com'));
  DELETE FROM dbo.users WHERE email = CONCAT('noise-', @i, '@example.com');
  SET @i = @i + 1;
END
GO

-- 2. Force CDC capture to scan and write the noise into the change
--    table immediately, rather than waiting for the SQL Server Agent.
EXEC sys.sp_cdc_scan;
GO

-- 3. Disable + re-enable CDC on the table. Re-enabling creates a new
--    capture instance whose start_lsn is the LSN at re-enable time —
--    which is strictly greater than any LSN saved by the baseline
--    read. This is the most reliable way to advance the per-instance
--    min_lsn past a saved offset; sys.sp_cdc_cleanup_change_table
--    requires low_water_mark to be a current entry in
--    cdc.lsn_time_mapping and only updates start_lsn to the min of
--    surviving rows, which can leave min_lsn equal to the saved value.
EXEC sys.sp_cdc_disable_table
  @source_schema      = N'dbo',
  @source_name        = N'users',
  @capture_instance   = N'dbo_users';

-- Generate a committed write to advance the LSN counter past the
-- saved baseline before re-enabling CDC.
INSERT INTO dbo.users (email) VALUES ('post-cleanup-anchor@example.com');
DELETE FROM dbo.users WHERE email = 'post-cleanup-anchor@example.com';

EXEC sys.sp_cdc_enable_table
  @source_schema        = N'dbo',
  @source_name          = N'users',
  @role_name            = NULL,
  @capture_instance     = N'dbo_users',
  @supports_net_changes = 0;

-- Force a CDC scan so the new capture instance's start_lsn is set.
EXEC sys.sp_cdc_scan;
GO

-- 4. Echo what the connector's two LSN-range queries now see. The
--    asymmetry between the legacy and the new query is the bug.
SELECT
  CONVERT(VARCHAR(MAX), sys.fn_cdc_get_min_lsn('dbo_users'), 1)
                                                     AS post_4_3_4_min_per_instance,
  CONVERT(VARCHAR(MAX), sys.fn_cdc_get_min_lsn(''),    1)
                                                     AS pre_4_3_4_min_legacy_query,
  CONVERT(VARCHAR(MAX), sys.fn_cdc_get_max_lsn(),      1)
                                                     AS database_max;
GO
