JSON Metadata Agent for Plex
============================

A metadata agent for Plex that reads from JSON files co-located with your media.


Why?
----

Not all metadata is easily accessed online via an HTML web page. There are some websites for which it is impossible to write a traditional Plex metadata agent — for example, those that:

* require username and password authentication, possibly even captcha
* hide information behind javascript
* detect the automated nature of the metadata agent, throttling or blocking scrapers
* perform poorly, crash and timeout
* frequently change their HTML structure

This agent doesn't collect any metadata itself — it simply loads metadata from JSON files found with your media into Plex.

It's designed to work alongside other tools and methods of collecting metadata, be it a custom scraper (it doesn't even have to be written in Python), browser plugin, command line tool or GUI. You could even edit the files by hand :)


Media Preperation
-----------------

At the time of writing, JSON metadata is supported *for movies only*.

To define metadata for a movie, a JSON file named exactly `Info.json` must be present in the same directory as your movie file(s). For example:

```
Movies
  |- Akira (1988)
      |- akira.1988.720p.bluray.x264.mp4
      |- Info.json
      |- Poster.jpg
```

This means you are limited to a single movie and `Info.json` file per directory.


Example JSON
------------

The structure of the `Info.json` file follows as closely as possible that of the `Movie` model defined by Plex itself (although it's basically undocumented). It should look something like this:

```json
{
	"title": "Akira",
    "summary": "Childhood friends Tetsuo and Kaneda are pulled into the...",
    "year": 1988,
    "rating": 7.7,
    "content_rating": "M",
    "studio": "Bandai Visual Company",
    "duration": 124,
    "directors": [
      "Katsuhiro Ōtomo"
    ],
    "roles": [
    	{
        	"actor": "Mitsuo Iwata",
            "role": "Shôtarô Kaneda"
        },
    ],
    "genres": [
    	"Animation",
        "Science Fiction"
    ],
    "collections": [
    	"Anime"
    ]
}
```
