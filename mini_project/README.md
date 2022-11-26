# Instructions

## ElasticSearch

### Start

```bash
cd mini_project/es-docker
docker-compose up -d
```

### Add Documents

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

### Explain Query

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

### Twitter Query

```json
PUT twitter/_mapping
{
  "properties": {
    "text": {
      "type":     "text",
      "fielddata": true
    }
  }
}

GET /_search
{
  "aggs": {
    "texts": {
      "terms": { "field": "text" }
    }
  }
}

GET /_search
{
  "query": {
    "terms": { "text": [ "zoom", "computer", "remote"] }
  },
  "aggregations": {
    "significant_crime_types": {
      "significant_terms": { "field": "text" }
    }
  }
}
```

## PostgreSQL

### Start

```bash
cd mini_project/psql-docker
docker-compose up -d
docker exec -it postgres_container bash
psql -U postgres
```

### Add Documents

```sql
create table ts(doc text, doc_tsv tsvector);

insert into ts(doc) values
  ('Can a sheet slitter slit sheets?'),
  ('How many sheets could a sheet slitter slit?'),
  ('I slit a sheet, a sheet I slit.'),
  ('Upon a slitted sheet I sit.'),
  ('Whoever slit the sheets is a good sheet slitter.'),
  ('I am a sheet slitter.'),
  ('I slit sheets.'),
  ('I am the sleekest sheet slitter that ever slit sheets.'),
  ('She slits the sheet she sits on.');

update ts set doc_tsv = to_tsvector(doc);

create index on ts using gin(doc_tsv);

select ctid, left(doc,20), doc_tsv from ts;
```

### Query

```sql
select doc from ts where doc_tsv @@ to_tsquery('many & slitter');
```
