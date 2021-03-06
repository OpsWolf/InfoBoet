# coding=utf-8
import ConfigParser
import json
import urllib
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def run(keyConfig, message, totalResults=1):
    requestText = str(message).strip()
    keyConfig = ConfigParser.ConfigParser()
    keyConfig.read(["keys.ini", "..\keys.ini"])

    trackUrl = 'http://api.musixmatch.com/ws/1.1/track.search?apikey='
    data = json.load(urllib.urlopen(trackUrl + keyConfig.get('MusixMatch', 'APP_ID') + '&q=' + requestText))
    if 'message' in data and \
                    'body' in data['message'] and \
                    'track_list' in data['message']['body'] and \
                    len(data['message']['body']['track_list']) >= 1 and \
                    'track' in data['message']['body']['track_list'][0] and \
                    'artist_name' in data['message']['body']['track_list'][0]['track'] and \
                    'track_name' in data['message']['body']['track_list'][0]['track'] and \
                    'track_id' in data['message']['body']['track_list'][0]['track']:
        artist_name = data['message']['body']['track_list'][0]['track']['artist_name']
        track_name = data['message']['body']['track_list'][0]['track']['track_name']
        if 'track_soundcloud_id' in data['message']['body']['track_list'][0]['track'] and str(data['message']['body']['track_list'][0]['track']['track_soundcloud_id']) != '':
            track_soundcloud_id = str(data['message']['body']['track_list'][0]['track']['track_soundcloud_id'])
        else:
            track_soundcloud_id = '0'
        trackId = str(data['message']['body']['track_list'][0]['track']['track_id'])
        lyricsUrl = 'http://api.musixmatch.com/ws/1.1/track.lyrics.get?apikey='
        data = json.load(urllib.urlopen(lyricsUrl + keyConfig.get('MusixMatch', 'APP_ID') + '&track_id=' + trackId))
        lyrics_body = ''
        if 'message' in data and \
                        'body' in data['message'] and \
                        'lyrics' in data['message']['body'] and \
                        len(data['message']['body']['lyrics']) >= 1 and \
                        'lyrics_body' in data['message']['body']['lyrics']:
            lyrics_body = data['message']['body']['lyrics']['lyrics_body'].replace(
                '******* This Lyrics is NOT for Commercial use *******\n(1409612423371)', '').replace('*','').replace(requestText,'*' + requestText + '*')
        FormattedResponse = track_name + ' by ' + artist_name + (('\nListen at: https://api.soundcloud.com/tracks/' + track_soundcloud_id) if not track_soundcloud_id == '0' else '') + (('\n' + lyrics_body) if not lyrics_body == '' else '')
        result = str(FormattedResponse)[:4093] + ('...' if len(FormattedResponse) > 4093 else '')
    else:
        result = 'I\'m sorry Dave, I\'m afraid I can\'t find any tracks for the lyrics ' + str(requestText)
    return result