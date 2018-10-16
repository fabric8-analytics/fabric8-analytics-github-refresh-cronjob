# GitHub refresh cronjob

OpenShift cron job for refreshing GitHub data of ingested packages.


## Configuration

Following environment variables can be used to control behaviour of the cron job:

`REFRESH_INTERVAL` - how often to refresh GitHub data, default: 14 days
