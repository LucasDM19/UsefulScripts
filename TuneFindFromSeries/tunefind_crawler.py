"""
Download all songs of a TV show from youtube as mp3. Can also download individual songs.

It all started with How I met your mother. As is well known, their music choice is excellent. So I wanted to download all the songs that appeared in HIMYM. So I wrote the following code. For actual download, it queues the url in IDM. You have to start those manually. Use cases are at the end of the code. We'll get to the code later, first an explanation. 

The site TuneFind lists music of Movies and TV shows, I extract the season list, episode list per season and songs list per episode from there.
Now that I have the name of the song and the artist, I get the first search result on youtube with these keywords.
Now that I have a youtube video id for a song, I send a request to YouTube to MP3 Converter to convert it to mp3 and get the url of the converted mp3.
Download the mp3 in the correct heirarchical location.

Finally, all the mp3s are downloaded and saved in respective folders for each episode for each season: 
"""
import os
import urllib.request, urllib.parse, urllib.error
import re
import pickle
import html.parser
import requests
import time
show_url = "http://www.tunefind.com/show/%s"
season_url = "http://www.tunefind.com/show/%s/season-%d"
episode_url = "http://www.tunefind.com/show/%s/season-%d/%s"
def get_youtube_mp3_url(url):
    for i in range(2):
        statusurl = None
        r = requests.post("http://www.listentoyoutube.com/cc/conversioncloud.php", data={"mediaurl": url, "client_urlmap": "none"})
        try:
            statusurl = eval(r.text)['statusurl'].replace('\\/', '/') + "&json"
            break
        except:
            print(eval(r.text)['error'])
            time.sleep(1)
    while True:
        if not statusurl:
            raise Exception("")
        try:
            resp = eval(requests.get(statusurl).text)
            if 'downloadurl' in resp:
                downloadurl = resp['downloadurl'].replace('\\/', '/')
                break
            time.sleep(1)
        except Exception:
            pass
    return downloadurl
def urlopen(url, tries=10):
    exc = "Couldn't open url %s" % url
    for i in range(tries):
        try:
            #stream = urllib.request.urlopen(url) #Maneira antiga
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'} ) #Sem isso fica com 403 - Forbidden
            stream = urllib.request.urlopen(req) #.read()
            return str(stream.read())
        except Exception as e:
            exc = e
    raise Exception(exc)
def download_song(song, location):
    print(song)
    song_name = song[1] + " - " + song[0] + ".mp3"
    if not os.path.exists(location):
        os.makedirs(location)
    if not os.path.exists(os.path.join(location, song_name)):
        try:
            r = requests.get("YouTube", params={"search_query": "%s %s" % (song[1], song[0])}).text
            top_vid_id = re.findall(r'data-context-item-id="(.*?)"', r)[0]
            mp3_url = get_youtube_mp3_url("YouTube" + top_vid_id)
            #cmd = 'idman /d %s /p "%s" /f "%s" /a' % (mp3_url, os.path.join(os.getcwd(), location), song_name) #Mudar AQUI
            #os.system(cmd)
            
            #Rotina que baixa um arquivo (no caso, MP3)
            #file_name = mp3_url.split('/')[-1]
            file_name = song_name
            u = urllib2.urlopen(mp3_url)
            f = open(file_name, 'wb')
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            print( "Downloading: %s Bytes: %s" % (file_name, file_size) )

            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)
                status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
                status = status + chr(8)*(len(status)+1)
                print (status),

            f.close()
            
        except Exception:
            raise
def get_episode_music(show, season, episode):
    episode_num, episode_name = episode
    episode_dir = os.path.join(show, str(season), episode_name.replace(':', ''))
    episode_data_path = os.path.join(show, str(season), episode_name.replace(':', ''), "data")
    if not os.path.exists(episode_dir):
        os.mkdir(episode_dir)
    if os.path.exists(episode_data_path):
        with open(episode_data_path) as episode_data_file:
            episode_data = pickle.load(episode_data_file)
    else:
        episode_data = {}
        pg = urlopen(episode_url % (show, season, episode_num))
        h = html.parser.HTMLParser()
        try:
            episode_data['songs'] = list((h.unescape(b), h.unescape(c), a) for (a, b, c, d) in re.findall(r'<a .*?name="song-\d+" href="(/song/\d+/\d+.*?)".*?><i.*?></i>(.*?)</a>\W*by (.*?)\W*<div.*?>\W*<div.*?>(.*?)</div>\W*</div>', pg))
        except:
            episode_data['songs'] = list((b, c, a) for (a, b, c, d) in re.findall(r'<a .*?name="song-\d+" href="(/song/\d+/\d+.*?)".*?><i.*?></i>(.*?)</a>\W*by (.*?)\W*<div.*?>\W*<div.*?>(.*?)</div>\W*</div>', pg))
        with open(episode_data_path, 'wb') as episode_data_file:
            pickle.dump(episode_data, episode_data_file)
    for song in episode_data['songs']:
        download_song(song, episode_dir)
def get_season_music(show, season):
    season_dir = os.path.join(show, str(season))
    season_data_path = os.path.join(show, str(season), 'data')
    if not os.path.exists(season_dir):
        os.mkdir(season_dir)
    if os.path.exists(season_data_path):
        with open(season_data_path, 'rb') as season_data_file:
            season_data = pickle.load(season_data_file)
    else:
        season_data = {}
        h = html.parser.HTMLParser()
        #print(season_url % (show, season))
        pg = urlopen(season_url % (show, season))
        #season_data['episodes'] = list((a, h.unescape(b)) for (a, b) in re.findall(r'<a href=".*?" name="episode(.*?)">\W*(.*?)\W*</a>', pg))
        season_data['episodes'] = list((a, h.unescape(b)) for (a, b) in re.findall(r'<a href=".*?" data-reactid=".*?">\W*(.*?)\W*</a>', pg))
        with open(season_data_path, 'wb') as season_data_file:
            pickle.dump(season_data, season_data_file)
    print( season_data )
    x = 1/0
    print("Temporada#", season, ", total de episodios=", len(season_data['episodes']) ) 
    for episode in season_data['episodes']:
        get_episode_music(show, season, episode)
def get_show_music(show):
    if not os.path.exists(show):
        os.mkdir(show)
    if os.path.exists(os.path.join(show, 'data')):
        with open(os.path.join(show, 'data'), 'rb') as show_data_file:
            show_data = pickle.load(show_data_file)
    else:
        show_data = {}
        slug = show.lower().replace(' ', '-')
        #pg = urlopen(show_url % show).read().decode('utf-8')
        pg = urlopen(show_url % show) #.decode('utf-8')
        season_finder_pattern = r'/show/' + slug + r'/season-\d+'
        print(season_finder_pattern)
        season_links = list(set(re.findall(season_finder_pattern, pg)))
        season_links.sort()
        seasons = list(int(sl[sl.find('season-') + len('season-'):]) for sl in season_links)
        seasons.sort()
        show_data['seasons'] = seasons
        with open(os.path.join(show, 'data'), 'wb') as show_data_file:
            pickle.dump(show_data, show_data_file)
    # print show_data
    print("Seriado=",show,", Temporadas=", len(show_data['seasons']) )
    for season in show_data['seasons']:
        get_season_music(show, season)
    os.system("idman /s")
if __name__ == '__main__':
    # download_song(["Humme hai hero", "A R Rahman"], "Misc")
    #download_song(["Caravan (Instrumental) [Remastered]","GORDON JENKINS"], "Misc")
    #get_show_music("How I Met Your Mother")
    get_show_music("Mad Men")