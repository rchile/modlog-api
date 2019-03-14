## /r/chile modlog API

This is a backend made on top of Flask. Retrieves modlog entries from the reddit API, 
and it works as a proxy for authentication. It is currently intended for usage
with the [/r/chile modlog site](https://rchile.xyz/modlog/). 

The output format is JSON, and it delivers the same format than the 
[reddit API for listings](https://www.reddit.com/dev/api/#listings).

Enrties have the following format:

```json
{
  "action": "removelink",
  "created_utc": 1551981075,
  "description": null,
  "details": "remove",
  "id": "ModAction_9a57a7e8-4101-11e9-807e-0ed31a2a60fc",
  "mod": "FeanDoe",
  "mod_id36": "rjsnu",
  "sr_id36": "2rer8",
  "subreddit": "chile",
  "subreddit_name_prefixed": "r/chile",
  "target_author": "Chrysheight",
  "target_body": null,
  "target_fullname": "t3_ayemjc",
  "target_permalink": "/r/chile/comments/ayemjc/carabinero_rescatando_perrito_en_raww/",
  "target_title": "Carabinero rescatando perrito en r/aww"
}
```

### Endpoints

#### `GET /`

It simply returns a 302 redirect to https://reddit.com/r/chile.

#### `GET /entries[/after/<entry_id>]`

Delivers a list of 100 entries at most. If the `/after/<entry_id>` section is not used,
then the list will begin with the latest entry. The `entry_id` parameter format is the same
as the `id` value seen on the entry example above. If it does not follow that format, a 400 
error is returned (Bad Request). The `ModAction_` part is optional.

#### `GET /entry/<entry_id>`

Tries to fetch a single entry. It searches the first entry `after` the selected one, then it 
fetches the previous one, effectively retrieving the selected one. It returns the single 
entry if found. or 404 if the entry was not found. Same as above, if the `entry_id` parameter 
does not follow the given format, it returns 400.

### Project file structure

* `app.py`: Main app module, implements the routes.
* `common.py`: Contains main methods for routes.
* `settings.example.py`: Contains variables to authenticate reddit API access.
* `requirements.txt`: pip modules requirements.
* `Procfile`: Allows this project to be run on Heroku.

#### Run the project

To locally run this project, you need to have Python 3.5+ and pip.

* Setup a `virtualenv` on the project root and enable it.
* Install project requirements from the `requirements.txt` file.
* Copy the `settings.example.py` file to `settings.py` and fill the parameters.
* Run the `app.py` file.

### TO-DO (future work)

* ~~Caching entries (database usage; note that entries doesn't change in time)~~
* Mod login and session support to add notes to entries
* Support for other reddit API parameters

### License

This software is licensed under the [MIT license](LICENSE.txt).
