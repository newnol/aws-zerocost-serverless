"""
Generate improved architecture diagram (horizontal layout) for the university project.

Usage:
    .venv-diagrams/bin/python scripts/generate_diagram_v3.py

Output:
    docs/architecture_v3.png
"""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.client import User


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
ICON_BASE = REPO_ROOT / "Icon-package_01302026.31b40d126ed27079b708594940ad577a86150582"


def icon(*parts: str) -> str:
    path = ICON_BASE.joinpath(*parts)
    if not path.exists():
        raise FileNotFoundError(path)
    return str(path)


ICONS = {
    "apigw": icon(
        "Architecture-Service-Icons_01302026",
        "Arch_Networking-Content-Delivery",
        "48",
        "Arch_Amazon-API-Gateway_48.png",
    ),
    "budgets": icon(
        "Architecture-Service-Icons_01302026",
        "Arch_Cloud-Financial-Management",
        "48",
        "Arch_AWS-Budgets_48.png",
    ),
    "cloudfront": icon(
        "Architecture-Service-Icons_01302026",
        "Arch_Networking-Content-Delivery",
        "48",
        "Arch_Amazon-CloudFront_48.png",
    ),
    "cloudwatch": icon(
        "Architecture-Service-Icons_01302026",
        "Arch_Management-Tools",
        "48",
        "Arch_Amazon-CloudWatch_48.png",
    ),
    "dynamodb": icon(
        "Architecture-Service-Icons_01302026",
        "Arch_Databases",
        "48",
        "Arch_Amazon-DynamoDB_48.png",
    ),
    "iam_role": icon(
        "Resource-Icons_01302026",
        "Res_Security-Identity",
        "Res_AWS-Identity-Access-Management_Role_48.png",
    ),
    "lambda": icon(
        "Architecture-Service-Icons_01302026",
        "Arch_Compute",
        "48",
        "Arch_AWS-Lambda_48.png",
    ),
    "router": icon(
        "Resource-Icons_01302026",
        "Res_Networking-Content-Delivery",
        "Res_Amazon-VPC_Router_48.png",
    ),
    "s3": icon(
        "Resource-Icons_01302026",
        "Res_Storage",
        "Res_Amazon-Simple-Storage-Service_S3-Standard_48.png",
    ),
    "sns": icon(
        "Architecture-Service-Icons_01302026",
        "Arch_Application-Integration",
        "48",
        "Arch_Amazon-Simple-Notification-Service_48.png",
    ),
    "subnet": icon(
        "Architecture-Group-Icons_01302026",
        "Private-subnet_32.png",
    ),
    "vpc": icon(
        "Resource-Icons_01302026",
        "Res_Networking-Content-Delivery",
        "Res_Amazon-VPC_Virtual-private-cloud-VPC_48.png",
    ),
    "vpce": icon(
        "Resource-Icons_01302026",
        "Res_Networking-Content-Delivery",
        "Res_Amazon-VPC_Endpoints_48.png",
    ),
}


GRAPH_ATTR = {
    "fontname": "Arial",
    "fontsize": "24",
    "labelloc": "t",
    "pad": "0.8",
    "ranksep": "2.0",
    "nodesep": "1.5",
    "splines": "spline",
    "bgcolor": "#ffffff",
}

NODE_ATTR = {
    "fontname": "Arial",
    "fontsize": "13",
    "margin": "0.3",
    "shape": "box",
    "style": "rounded",
}

EDGE_ATTR = {
    "fontname": "Arial",
    "fontsize": "11",
    "penwidth": "2.0",
}


def cluster_style(bg: str, border: str, label_color: str = "#000000") -> dict[str, str]:
    return {
        "bgcolor": bg,
        "pencolor": border,
        "fontcolor": label_color,
        "fontsize": "18",
        "labeljust": "l",
        "margin": "30",
        "penwidth": "2.5",
        "style": "rounded,filled",
    }


# Color scheme
AWS_CLOUD = cluster_style("#F5F5F5", "#232F3E", "#232F3E")
VPC_CLUSTER = cluster_style("#E8F5E9", "#2E7D32", "#1B5E20")
SUBNET_CLUSTER = cluster_style("#E3F2FD", "#1565C0", "#0D47A1")
FRONTEND_CLUSTER = cluster_style("#FFF3E0", "#E65100", "#BF360C")
API_CLUSTER = cluster_style("#F3E5F5", "#6A1B9A", "#4A148C")
MONITORING_CLUSTER = cluster_style("#FCE4EC", "#C2185B", "#880E4F")


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    with Diagram(
        "AWS Zero-Cost Serverless Architecture",
        filename=str(DOCS_DIR / "architecture_v3"),
        outformat="png",
        show=False,
        direction="LR",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        user = User("User\nBrowser")

        with Cluster("AWS Cloud", graph_attr=AWS_CLOUD):
            
            # Frontend Section
            with Cluster("Frontend Layer", graph_attr=FRONTEND_CLUSTER):
                cloudfront = Custom("CloudFront\nCDN", ICONS["cloudfront"])
                s3 = Custom("S3 Bucket\nPrivate + OAC", ICONS["s3"])
                cloudfront >> Edge(label="OAC", color="#FF6F00", penwidth="2.5") >> s3

            # API Section
            with Cluster("API Layer", graph_attr=API_CLUSTER):
                api_gateway = Custom("API Gateway\nREST API", ICONS["apigw"])
                lambda_fn = Custom("Lambda\nPython 3.12", ICONS["lambda"])
                lambda_role = Custom("IAM Role\nLeast Privilege", ICONS["iam_role"])
                
                api_gateway >> Edge(label="Invoke", color="#7B1FA2", penwidth="2.5") >> lambda_fn
                lambda_role >> Edge(label="Assume", color="#9C27B0", style="dashed") >> lambda_fn

            # VPC Section
            with Cluster("VPC (10.0.0.0/16)", graph_attr=VPC_CLUSTER):
                
                with Cluster("AZ-A", graph_attr=SUBNET_CLUSTER):
                    subnet_a = Custom("Private\n10.0.1.0/24", ICONS["subnet"])
                
                with Cluster("AZ-B", graph_attr=SUBNET_CLUSTER):
                    subnet_b = Custom("Private\n10.0.2.0/24", ICONS["subnet"])
                
                route_table = Custom("Route Table\nPrivate", ICONS["router"])
                vpce_ddb = Custom("VPC Endpoint\nDynamoDB", ICONS["vpce"])
                
                lambda_fn >> Edge(label="VPC Config", color="#2E7D32", penwidth="2.5") >> subnet_a
                lambda_fn >> Edge(label="VPC Config", color="#2E7D32", penwidth="2.5") >> subnet_b
                
                subnet_a >> Edge(color="#388E3C", style="dashed") >> route_table
                subnet_b >> Edge(color="#388E3C", style="dashed") >> route_table
                route_table >> Edge(label="Private", color="#43A047", penwidth="3.0") >> vpce_ddb

            # Database
            dynamodb = Custom("DynamoDB\nTasks + GSI", ICONS["dynamodb"])
            vpce_ddb >> Edge(label="AWS Backbone\nNo Internet", color="#00C853", penwidth="3.0") >> dynamodb

            # Monitoring Section
            with Cluster("Monitoring", graph_attr=MONITORING_CLUSTER):
                cloudwatch = Custom("CloudWatch\nLogs + Metrics", ICONS["cloudwatch"])
                sns = Custom("SNS\nEmail", ICONS["sns"])
                budgets = Custom("Budgets\n$0.01", ICONS["budgets"])
                
                cloudwatch >> Edge(label="Alarm", color="#C2185B", style="dashed") >> sns
                budgets >> Edge(label="Alert", color="#C2185B", style="dashed") >> sns

            # User connections
            user >> Edge(label="HTTPS\nStatic", color="#FF6F00", penwidth="2.5") >> cloudfront
            user >> Edge(label="HTTPS\nAPI", color="#7B1FA2", penwidth="2.5") >> api_gateway

            # Monitoring connections
            lambda_fn >> Edge(label="Logs", color="#D81B60", style="dashed") >> cloudwatch
            api_gateway >> Edge(label="Metrics", color="#D81B60", style="dashed") >> cloudwatch

    print("[✓] Generated docs/architecture_v3.png")


if __name__ == "__main__":
    main()
