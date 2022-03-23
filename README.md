# FRC2022Stats
This is a little Python program I wrote to analyze data downloaded from The Blue Alliance's API. To download the json file for an event, run `curl -H "X-TBA-Auth-Key: <INSERT API KEY>" https://www.thebluealliance.com/api/v3/event/<event_code>/matches > all_<event>_matches.json` and then analyze it with `python3 parse.py <event>`
