# Collection Log Troubleshooting

Use this guide when the Reddit collection pipeline fails or produces unexpected output.

## Common Issues

### 1. Authentication Failure
- Verify `.env` exists and contains `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, and `REDDIT_USER_AGENT`
- Confirm the Reddit app was created at https://www.reddit.com/prefs/apps
- Ensure the user agent string is unique and descriptive

### 2. Rate Limit or Temporary API Errors
- Re-run the batch job after a short pause
- Lower `REQUEST_INTERVAL_SECONDS` in `.env` only if the API is stable
- Check `collection_log` for repeated 429 or 503 errors

### 3. Duplicate Records
- Confirm the database schema was initialized with the `data_hash` unique constraint
- Verify the batch job is not running more than once at the same time
- Inspect `collection_log` for duplicate count spikes

### 4. Empty Dataset
- Confirm the target subreddit list is populated in `.env`
- Check that `COMMENTS_PER_SUBREDDIT` is greater than zero
- Make sure `data/comments.db` was created successfully

## Useful Checks

```bash
python database.py
python batch_job.py
```

```sql
SELECT * FROM collection_log ORDER BY run_timestamp DESC LIMIT 5;
SELECT COUNT(*) FROM comments;
SELECT COUNT(*) FROM model_mentions;
```

## Recovery Steps

If the pipeline state becomes inconsistent, you can reset the local database and start over:

```sql
DELETE FROM model_mentions;
DELETE FROM comments;
DELETE FROM collection_log;
```
