import os, json
import urllib

class JSONAgent(Agent.TV_Shows):
    name = 'Personal Shows'
    languages = [Locale.Language.NoLanguage]
    primary_provider = True
    persist_stored_files = False

    def search(self, results, media, lang):
        Log('I am here')
        Log(media.show)
        Log(media.episode)
        Log(media.season)
        Log(media.name)
        Log(media.filename)
        
        
        x = "My Title %s %s %s" % (media.name, media.episode, media.season)
        results.Append(MetadataSearchResult(id = media.filename, score = 100, name=media.filename, lang=Locale.Language.NoLanguage))

    def update_season(self, season_id, summary):
        ip_address = Prefs['ip_address']
        port = Prefs['port']
        username = Prefs['username']
        password = Prefs['password']
        host = '%s:%s' % (ip_address, port)
        HTTP.SetPassword(host, username, password)

        metadata = json.loads(HTTP.Request(url=('http://%s/library/metadata/%s' %(host, season_id)), immediate=True, headers={'Accept': 'application/json'}).content)
        section_id = metadata['MediaContainer']['librarySectionID']
        Log('sectionId')
        Log(section_id)
        request = HTTP.Request(url=('http://%s/library/sections/%s/all?summary.value=%s&type=3&id=%s' % (host, section_id, urllib.quote(summary), season_id)), method='PUT' )
        
        request.load()
        response = request.content
        Log(response)


    def update(self, metadata, media, lang):
        Log('I am in update')
        
        Log(dir(media.seasons['1']))
        Log(media.seasons['1'].title)
        main_path = media.seasons['1'].episodes['1'].items[0].parts[0].file
        Log(main_path)
        show_path = os.path.normpath(os.path.join(main_path, '../../'))
        show_name = os.path.basename(show_path)
        metadata.title = show_name

        meta_path = os.path.join(show_path, 'meta.json')
        meta_json = json.loads(Core.storage.load(meta_path))
        Log(meta_json)
        metadata.posters[meta_json['show_thumbnail']] = Proxy.Preview(None)
        metadata.genres.clear()
        for genre in meta_json['tags']:
            metadata.genres.add(genre)
        metadata.studio = meta_json['publisher']
    
        for season_index in media.seasons.keys():
            metadata.seasons[season_index].posters[meta_json['season_thumbnails'][season_index]] = Proxy.Preview(None)
            season_path = os.path.normpath(os.path.join(main_path, '../'))
            metadata.seasons[season_index].summary = os.path.basename(season_path)
            self.update_season(media.seasons[season_index].id, os.path.basename(season_path))
            for episode_index in media.seasons[season_index].episodes.keys():
                episode_path = media.seasons[season_index].episodes[episode_index].items[0].parts[0].file
                episode_file_name = os.path.basename(episode_path)
                episode_name = os.path.splitext(episode_file_name)[0]
                metadata.seasons[season_index].episodes[episode_index].title = episode_name