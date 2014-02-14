#!/usr/bin/python

from datetime import datetime, timedelta
import httplib2
import os
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run
from optparse import OptionParser



# CLIENT_SECRETS_FILE, name of a file containing the OAuth 2.0 information for
# this application, including client_id and client_secret. You can acquire an
# ID/secret pair from the API Access tab on the Google APIs Console
#   http://code.google.com/apis/console#access
# For more information about using OAuth2 to access Google APIs, please visit:
#   https://developers.google.com/accounts/docs/OAuth2
# For more information about the client_secrets.json file format, please visit:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
# Please ensure that you have enabled the YouTube Data & Analytics APIs for your project.
CLIENT_SECRETS_FILE = "client_secrets.json"

# We will require read-only access to the YouTube Data and Analytics API.
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
  "https://www.googleapis.com/auth/yt-analytics.readonly"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_ANALYTICS_API_SERVICE_NAME = "youtubeAnalytics"
YOUTUBE_ANALYTICS_API_VERSION = "v1"

# Helpful message to display if the CLIENT_SECRETS_FILE is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the APIs Console
https://code.google.com/apis/console#access

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

now = datetime.now()
one_day_ago = (now - timedelta(days=1)).strftime("%Y-%m-%d")
one_week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")

parser = OptionParser()
parser.add_option("--metrics", dest="metrics", help="Report metrics",
  default="views,comments,favoritesAdded,favoritesRemoved,likes,dislikes,shares")
parser.add_option("--dimensions", dest="dimensions", help="Report dimensions",
  default="video")
parser.add_option("--start-date", dest="start_date",
  help="Start date, in YYYY-MM-DD format", default=one_week_ago)
parser.add_option("--end-date", dest="end_date",
  help="End date, in YYYY-MM-DD format", default=one_day_ago)
parser.add_option("--start-index", dest="start_index", help="Start index",
  default=1, type="int")
parser.add_option("--max-results", dest="max_results", help="Max results",
  default=10, type="int")
parser.add_option("--sort", dest="sort", help="Sort order", default="-views")
(options, args) = parser.parse_args()

flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
  message=MISSING_CLIENT_SECRETS_MESSAGE,
  scope=" ".join(YOUTUBE_SCOPES))

storage = Storage("%s-oauth2.json" % sys.argv[0])
credentials = storage.get()

if credentials is None or credentials.invalid:
  credentials = run(flow, storage)

http = credentials.authorize(httplib2.Http())
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=http)
youtube_analytics = build(YOUTUBE_ANALYTICS_API_SERVICE_NAME,
  YOUTUBE_ANALYTICS_API_VERSION, http=http)



# What does my playlists contain?
print("Fetching playlists")
playlists = youtube.playlists().list(
    mine=True,
    part="snippet").execute()
    
fh = open('playlists.txt', 'w')
fh.write("playlistId,playlistTitle,videoId\n")
for item in playlists["items"]:
    playlistId = item["id"]
    playlistTitle = item["snippet"]["title"]
    #print("id: %s" % playlistId)
    #print("title: %s" % playlistTitle)
    
    next_page_token = ""
    while next_page_token is not None:
        elementsInPlaylist = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=item["id"],
            pageToken=next_page_token).execute()

        for playlistItem in elementsInPlaylist["items"]:
            videoId = playlistItem["contentDetails"]["videoId"]
            playlistIdAscii = playlistId.encode('utf-8')
            playlistTitleAscii = playlistTitle.encode('utf-8', 'ignore')
            videoIdAscii = videoId.encode('utf-8')
            fh.write("%s,\"%s\",%s\n" % (playlistIdAscii, playlistTitleAscii, videoIdAscii))
        
        next_page_token = elementsInPlaylist.get(
            "nextPageToken")
fh.close()


# Iterate through all my videos
print("Get view statistics for all my videos")
channels_response = youtube.channels().list(
  mine=True,
  part="contentDetails"
).execute()

datesAndViews = []
videoIdsAndTitles = []

for channel in channels_response["items"]:
    channel_id = channel["id"]

    uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
    print "Channel id: %s" % uploads_list_id
    print "Videos in list %s" % uploads_list_id
    next_page_token = ""
    while next_page_token is not None:
        playlistitems_response = youtube.playlistItems().list(
        playlistId=uploads_list_id,
        part="snippet",
        maxResults=50,
        pageToken=next_page_token
        ).execute()

        for playlist_item in playlistitems_response["items"]:
            title = playlist_item["snippet"]["title"]
            video_id = playlist_item["snippet"]["resourceId"]["videoId"]
            print "%s (%s)" % (title, video_id)
            tempIdAndTitle = (video_id, title)
            videoIdsAndTitles.append(tempIdAndTitle)
            
            analytics_response = youtube_analytics.reports().query(
                ids="channel==%s" % channel_id,
                filters="video==%s" % video_id,
                metrics="estimatedMinutesWatched", # views, estimatedMinutesWatched
                dimensions="day",
                max_results=1000,
                sort="day",
                start_date="2012-01-01",
                end_date="2014-10-31"
            ).execute()
                                
            for row in analytics_response.get("rows", []):
                tempData = (video_id, title, row[0], row[1])
                datesAndViews.append(tempData)
            
            #if(len(videoIdsAndTitles) > 5):
            #    break
        #if(len(videoIdsAndTitles) > 5):
        #    break

        #quit()
        next_page_token = playlistitems_response.get("nextPageToken")

fh = open('videoIdsAndTitles.txt', 'w')
for data in videoIdsAndTitles:
    videoIdAscii = data[0].encode('utf-8', 'ignore')
    videoTitleAscii = data[1].encode('utf-8', 'ignore')
    fh.write("%s,\"%s\"\n" % (videoIdAscii, videoTitleAscii))
fh.close()
            
fh = open('datesAndViews.txt', 'w')
for data in datesAndViews:
    videoIdAscii = data[0].encode('utf-8', 'ignore')
    videoViewDateAscii = data[2].encode('utf-8', 'ignore')
    videoViews = data[3]
    fh.write("%s,%s,%d\n" % (videoIdAscii, videoViewDateAscii, videoViews))
fh.close()
