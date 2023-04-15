from elasticsearch import Elasticsearch
from sklearn.datasets import fetch_openml
from tqdm.auto import tqdm

es = Elasticsearch(hosts="http://localhost:9200")

if __name__ == "__main__":
    tweet_dataset = fetch_openml(data_id=43794, as_frame=True)

    for id, row in tqdm(
        tweet_dataset.data.iterrows(), total=tweet_dataset.data.shape[0]
    ):
        # Ingest to ElasticSearch
        es_response = es.index(
            index="twitter", document={"id": int(id), "text": row["Text"]}
        )
        if es_response["result"] != "created":
            raise RuntimeError(
                "ElasticSearch index error: {}".format(es_response["result"])
            )
