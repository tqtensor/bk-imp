from diagrams import Cluster, Diagram
from diagrams.aws.general import Marketplace
from diagrams.aws.ml import SagemakerModel
from diagrams.aws.storage import SimpleStorageServiceS3Bucket
from diagrams.custom import Custom
from diagrams.onprem.analytics import Spark
from diagrams.onprem.database import Neo4J
from diagrams.onprem.queue import Kafka
from diagrams.programming.language import Python

graph_attr = {
    "beautify": "true",
    "center": "true",
    "dpi": "300.0",
    "layout": "dot",
    "fontsize": "30",
}


with Diagram(
    "Graph-based RecSys",
    show=False,
    direction="LR",
    outformat="png",
    graph_attr=graph_attr,
):
    with Cluster("Batch Layer"):
        s3 = SimpleStorageServiceS3Bucket("AWS\nReview Dataset")
        model = SagemakerModel("Factorization\nMachine")
        batch_features = Custom(
            "Batch Features", "bigdata-mini-project/img/matrix.png"
        )

        with Cluster("Distributed Graph Engine"):
            spark = Spark("Spark")
            graphx = Custom("GraphX", "bigdata-mini-project/img/graphx.png")

            spark >> graphx >> spark

    with Cluster("Speed Layer"):
        graph_db = Neo4J("Neo4j")
        networkx = Python("NetworkX")
        online_features = Custom(
            "Online Features", "bigdata-mini-project/img/matrix.png"
        )
        trained_model = SagemakerModel("Trained\nModel")
        recommendation = Marketplace("Recommendation")

    kafka = Kafka("Kafka")

    (
        kafka
        >> graph_db
        >> networkx
        >> online_features
        >> trained_model
        >> recommendation
    )
    s3 >> spark >> batch_features >> model >> trained_model
