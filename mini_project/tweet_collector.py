import json
import os

from elasticsearch import Elasticsearch
import requests

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")

es = Elasticsearch(hosts="http://localhost:9200")


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth)
    if response.status_code != 200:
        raise Exception("Cannot get rules (HTTP {}): {}".format(
            response.status_code, response.text))
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload)
    if response.status_code != 200:
        raise Exception("Cannot delete rules (HTTP {}): {}".format(
            response.status_code, response.text))
    print(json.dumps(response.json()))


def set_rules(delete):
    # You can adjust the rules if needed
    sample_rules = [
        {
            "value":
                "(context:46.1557697333571112960) (place_country:US OR place_country:CA)"
        },
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception("Cannot add rules (HTTP {}): {}".format(
            response.status_code, response.text))
    print(json.dumps(response.json()))


def get_stream(set):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream",
        auth=bearer_oauth,
        stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception("Cannot get stream (HTTP {}): {}".format(
            response.status_code, response.text))
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            print(json_response)
            # Ingest to ElasticSearch
            es_response = es.index(index="twitter",
                                   document={
                                       "id": json_response["data"]["id"],
                                       "text": json_response["data"]["text"]
                                   })
            if es_response['result'] != "created":
                raise RuntimeError("ElasticSearch index error: {}".format(
                    es_response['result']))


def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    while True:
        get_stream(set)


if __name__ == "__main__":
    main()
