# Add Documents
```json
PUT bk_imp/_doc/0
{
  "id": "c",
  "title": "video game history"
}

PUT bk_imp/_doc/1
{
  "id": "a",
  "title": "game video review game"
}

PUT bk_imp/_doc/2
{
  "id": "b",
  "title": "game store"
}

GET bk_imp/_search
{
  "query": {
    "match_all": {}
  }
}
```

# Explain Query
```json
GET /_search
{
  "query": {
    "match": {
      "title": {
        "query": "game"
      }
    }
  }
}

GET /bk_imp/_explain/1
{
  "query": {
    "match": {
      "title": "game"
    }
  }
}
```
