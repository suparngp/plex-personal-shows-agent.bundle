import os, json
import urllib
import hashlib
from Helpers import clear_posters

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

    def update_poster(self, metadata, link, base_path = None):
        try:
            Log.Info('Updating poster link: %s base: %s' % (link, base_path))
            if not link or not metadata:
                Log.Info('Skipping poster update. Link or metadata missing')
                return
            
            if link.startswith('http://') or link.startswith('https://'):
                metadata.posters[link] = Proxy.Preview(None)
                return
            
            if not link.startswith('/') and not base_path:
                Log.Info('Skipping poster update, link is relative and base path is missing')
                return
            
            if link.startswith('/'):
                poster_path = link
            else:
                poster_path = os.path.normpath(os.path.join(base_path, link))
                if not os.path.exists(poster_path):
                    poster_path = os.path.normpath(os.path.join(base_path, '../', link))
            
            Log.Info('Poster path %s' % (poster_path))
            data = Core.storage.load(poster_path)
            media_hash = hashlib.md5(data).hexdigest()
            metadata.posters[media_hash] = Proxy.Media(data)
        except Exception as e:
            Log.Error('Error updating poster %s' % e.message)

    def update(self, metadata, media, lang):
        Log.Info('Updating Metadata')
        
        main_path = media.seasons['1'].episodes['1'].items[0].parts[0].file

        show_path = os.path.normpath(os.path.join(main_path, '../'))
        meta_path = os.path.join(show_path, 'meta.json')

        if not os.path.exists(meta_path):
            show_path = os.path.normpath(os.path.join(main_path, '../../'))
            meta_path = os.path.join(show_path, 'meta.json')
        
        show_name = os.path.basename(show_path)
        metadata.title = show_name

        if os.path.exists(meta_path):
            meta_json = json.loads(Core.storage.load(meta_path))
            Log.Info(meta_json)
            metadata.summary = meta_json.get('summary', '')
            metadata.studio = meta_json.get('publisher', '')
            
            metadata.originally_available_at = Datetime.ParseDate(meta_json.get('available_date', '1900-01-01')).date()
            metadata.collections.clear()
            for collections in meta_json.get('collections', []):
                metadata.collections.add(collections)

            metadata.genres.clear()
            for genre in meta_json.get('tags', []):
                metadata.genres.add(genre)

            metadata.roles.clear()
            for actor in meta_json.get('actors', []):
                role = metadata.roles.new()
                role.role = actor.get('role', '')
                role.name = actor.get('name', '')
                role.photo = actor.get('photo', '')
            
            clear_posters(metadata)
            self.update_poster(metadata, meta_json.get('show_thumbnail', 'cover.jpg'), show_path)

        for season_index in media.seasons.keys():
            season_metadata = metadata.seasons[season_index]
            episode_keys = media.seasons[season_index].episodes.keys()
            first_episode_path = media.seasons[season_index].episodes[episode_keys[0]].items[0].parts[0].file
            season_path = os.path.normpath(os.path.join(first_episode_path, '../'))
            season_name = os.path.basename(season_path)

            season_summary = season_name
            
            clear_posters(season_metadata)
            if meta_json and 'seasons' in meta_json and season_index in meta_json['seasons']:
                season_meta_json = meta_json['seasons'][season_index]
                
                self.update_poster(season_metadata, season_meta_json.get('poster', 'cover.jpg'), season_path)
                season_summary = ('%s\n%s' % (season_name, meta_json['seasons'][season_index].get('summary', ''))).strip()                    
            else:
                self.update_poster(season_metadata, 'cover.jpg', season_path)
                
            season_metadata.summary = season_summary
            self.update_season(media.seasons[season_index].id, season_summary)
            
            for episode_index in media.seasons[season_index].episodes.keys():
                episode_metadata = season_metadata.episodes[episode_index]
                episode_path = media.seasons[season_index].episodes[episode_index].items[0].parts[0].file
                episode_file_name = os.path.basename(episode_path)
                filtered_name = os.path.splitext(episode_file_name)[0].replace('S%sE%s - ' % (season_index, episode_index), '')
                episode_name = '%s - %s' %(str(episode_index).zfill(2), filtered_name)
                episode_metadata.title = episode_name