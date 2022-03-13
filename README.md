## r/Chile Modlog API

Public API to read r/chile moderation log. Based on Flask and connected to our MongoDB database.
Endpoint responses are JSON, no authentication is required.

### `GET /`

Redirects to https://rchile.net/.

### `GET /api/entries`

Fetch modlog entries, which are sorted by date, from new to old. Returns an array (list) of entries, as
detailed in [Entry format](#entry-format).

#### Parameters

* `limit`: Amount of entries listed, 1 to 10, 20, 50 and 100.
* `automod`: If "0", it will filter out AutoModerator actions.
* `mod`: Filter by an specific moderator, using their username.
* `user`: Filter by an specific user target (target_user on the reddit API), using their username.
* `after`: The listed entries will be the ones after the selected one, by its ID ("id" field). If
the requested entry does not exist, this parameter is omitted.

### `GET /api/entries/<entry_id>`

Fetch an specific entry. If the entry is not found, status 404 is returned. If the entry ID is invalid,
then the status 400 is returned.

### Entry format

Entries are in the following format:

```json
{
    "action": "approvelink", 
    "created_utc": 1647181631.0, 
    "description": "", 
    "details": "unspam", 
    "id": "ModAction_ac023ec8-a2d9-11ec-97b3-aff4ee043f6e", 
    "mod": "makzk", 
    "mod_id36": "btyje", 
    "sr_id36": "2rer8", 
    "subreddit": "chile", 
    "subreddit_name_prefixed": "r/chile", 
    "target_author": "BlueVigilant", 
    "target_body": null, 
    "target_fullname": "t3_td7zxx", 
    "target_permalink": "/r/chile/comments/td7zxx/qu\u00e9_onda_en_youtube_estaba_haciendo_ejercicio_y/", 
    "target_title": "Qu\u00e9 onda en YouTube? Estaba haciendo ejercicio y me encuentro con esto"
}
```

#### Hidden entries

Sometimes, due to privacy reasons, we will need to hide entries content. Those entries will have the
following extra fields:

```json
{
    "hidden": true,
    "hidden_reason": "Contiene el número de teléfono de una persona"
}
```

Additionally, the following fields will be `null`:
>  `target_author`, `target_permalink`, `target_body`, `target_title`,
`target_fullname`, `description`, `details`.

### License

This software is licensed under the [MIT](LICENSE) license.
