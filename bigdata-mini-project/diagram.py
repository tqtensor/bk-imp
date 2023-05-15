from diagrams import Cluster, Diagram
from diagrams.aws.general import Marketplace
from diagrams.aws.ml import SagemakerModel
from diagrams.aws.storage import SimpleStorageServiceS3Bucket
from diagrams.custom import Custom
from diagrams.onprem.analytics import Spark
from diagrams.onprem.database import Neo4J
from diagrams.programming.language import Python

graph_attr = {
    "beautify": "true",
    "center": "true",
    "dpi": "300.0",
    "layout": "dot",
    "fontsize": "30",
}


with Diagram(
    "_________",
    show=False,
    direction="LR",
    outformat="png",
    graph_attr=graph_attr,
):
    with Cluster("Data Layer"):
        s3 = SimpleStorageServiceS3Bucket("AWS\nReview Dataset")
        graph_db = Neo4J("Neo4j")

    with Cluster("Batch Layer"):
        model = SagemakerModel("Recommendation\nModel")
        batch_features = Custom(
            "Batch Features", "bigdata-mini-project/img/matrix.png"
        )
        spark = Spark("Spark")

    with Cluster("Speed Layer"):
        networkx = Python("NetworkX")
        online_features = Custom(
            "Online Features", "bigdata-mini-project/img/matrix.png"
        )
        trained_model = SagemakerModel("Trained\nModel")
        recommendation = Marketplace("Recommendation")

    (
        graph_db
        >> networkx
        >> online_features
        >> trained_model
        >> recommendation
    )
    s3 >> spark >> batch_features >> model >> trained_model
    spark >> graph_db >> spark
