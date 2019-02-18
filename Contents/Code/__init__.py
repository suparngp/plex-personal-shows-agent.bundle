import os, json
import urllib

class PersonalShowsAgent(Agent.TV_Shows):
    name = 'Personal Shows'
    languages = [Locale.Language.NoLanguage]
    primary_provider = True
    persist_stored_files = False

    def search(self, results, media, lang):
        Log.Info('Searching Metadata')      
        x = "My Title %s %s %s" % (media.name, media.episode, media.season)
        results.Append(MetadataSearchResult(id = media.filename, score = 100, name=media.filename, lang=Locale.Language.NoLanguage))

    def update_season(self, season_id, summary):
        ip_address = Prefs['ip_address']
        port = Prefs['port']
        username = Prefs['username']
        password = Prefs['password']
        
        if not ip_address or not port or not username or not password:
            Log.Info('Missing Preferences, Skipping Summary Update')
            return

        host = '%s:%s' % (ip_address, port)
        HTTP.SetPassword(host, username, password)

        metadata = json.loads(HTTP.Request(url=('http://%s/library/metadata/%s' %(host, season_id)), immediate=True, headers={'Accept': 'application/json'}).content)
        section_id = metadata['MediaContainer']['librarySectionID']

        request = HTTP.Request(url=('http://%s/library/sections/%s/all?summary.value=%s&type=3&id=%s' % (host, section_id, urllib.quote(summary), season_id)), method='PUT' )        
        request.load()

    def update(self, metadata, media, lang):
        Log.Info('Updating Metadata')
        
        main_path = media.seasons['1'].episodes['1'].items[0].parts[0].file

        show_path = os.path.normpath(os.path.join(main_path, '../../'))
        show_name = os.path.basename(show_path)
        metadata.title = show_name

        meta_json = None
        meta_path = os.path.join(show_path, 'meta.json')
        if os.path.exists(meta_path):
            meta_json = json.loads(Core.storage.load(meta_path))
            Log.Info(meta_json)
            metadata.posters[meta_json.get('show_thumbnail', '')] = Proxy.Preview(None)
            metadata.studio = meta_json.get('publisher', '')
            metadata.genres.clear()
            for genre in meta_json.get('tags', []):
                metadata.genres.add(genre)

            metadata.roles.clear()
            for actor in meta_json.get('actors', []):
                role = metadata.roles.new()
                role.role = actor.get('role', '')
                role.name = actor.get('name', '')
                role.photo = actor.get('photo', '')
            
        for season_index in media.seasons.keys():
            season_metadata = metadata.seasons[season_index]
            episode_keys = media.seasons[season_index].episodes.keys()
            first_episode_path = media.seasons[season_index].episodes[episode_keys[0]].items[0].parts[0].file
            if meta_json:
                season_thumbs = meta_json.get('season_thumbnails')
                if season_thumbs:
                    season_metadata.posters[season_thumbs.get(season_index, '')] = Proxy.Preview(None)

            season_path = os.path.normpath(os.path.join(first_episode_path, '../'))
            season_metadata.summary = os.path.basename(season_path)
            self.update_season(media.seasons[season_index].id, os.path.basename(season_path))

            for episode_index in media.seasons[season_index].episodes.keys():
                episode_metadata = season_metadata.episodes[episode_index]
                episode_path = media.seasons[season_index].episodes[episode_index].items[0].parts[0].file
                episode_file_name = os.path.basename(episode_path)
                filtered_name = os.path.splitext(episode_file_name)[0].replace('S%sE%s - ' % (season_index, episode_index), '')
                episode_name = '%s - %s' %(str(episode_index).zfill(2), filtered_name)
                episode_metadata.title = episode_name