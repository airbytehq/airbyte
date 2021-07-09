delete from jobs where jobs.id in (
    select jobs.id  
    from jobs 
    left join (
           select scope, count(jobs.id) as jobCount from jobs group by scope
    ) counts on jobs.scope = counts.scope 
    where 
          -- job must be at least MINIMUM_AGE_IN_DAYS old or connection has more than EXCESSIVE_NUMBER_OF_JOBS 
      (jobs.created_at < (TO_TIMESTAMP(?, 'YYYY-MM-DD') - interval '%d' day) or counts.jobCount >  ?) 
    and jobs.id not in (
          -- cannot be the most recent job with saved state 
          select job_id as latest_job_id_with_state from (
              select jobs.scope, jobs.id as job_id, jobs.config_type, jobs.created_at, jobs.status, 
                bool_or(attempts."output" -> 'sync' -> 'state' -> 'state' is not null) as outputStateExists,
                row_number() OVER (PARTITION BY scope ORDER BY jobs.created_at desc, jobs.id desc) as stateRecency
              from jobs 
              left join attempts on jobs.id = attempts.job_id 
              group by scope, jobs.id
              having bool_or(attempts."output" -> 'sync' -> 'state' -> 'state' is not null) = true
              order by scope, jobs.created_at desc, jobs.id desc
           ) jobs_with_state where stateRecency=1
    ) and jobs.id not in (
          -- cannot be one of the last MINIMUM_RECENCY jobs for that connection/scope
          select id from (
                select jobs.scope, jobs.id, jobs.created_at,
                row_number() OVER (PARTITION BY scope ORDER BY jobs.created_at desc, jobs.id desc) as recency
                from jobs
                group by scope, jobs.id
                order by scope, jobs.created_at desc, jobs.id desc
          ) jobs_by_recency 
          where recency <= ?
    )
)
