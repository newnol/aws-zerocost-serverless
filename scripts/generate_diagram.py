"""
Generate the architecture diagram for the university project.

Usage:
    .venv-diagrams/bin/python scripts/generate_diagram.py

Output:
    docs/architecture.png
"""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.generic.blank import Blank
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
    "compound": "true",
    "fontname": "Helvetica",
    "fontsize": "20",
    "labelloc": "t",
    "newrank": "true",
    "nodesep": "0.9",
    "pad": "0.45",
    "ranksep": "1.15",
    "splines": "ortho",
}

NODE_ATTR = {
    "fontname": "Helvetica",
    "fontsize": "12",
    "margin": "0.20",
}

EDGE_ATTR = {
    "fontname": "Helvetica",
    "fontsize": "10",
    "penwidth": "1.6",
}


def cluster_style(bg: str, border: str) -> dict[str, str]:
    return {
        "bgcolor": bg,
        "color": border,
        "fontcolor": "#1f2937",
        "fontsize": "16",
        "margin": "18",
        "pencolor": border,
        "penwidth": "1.2",
        "style": "rounded,filled",
    }


AWS_CLOUD = cluster_style("#eef6ff", "#bfd5ea")
SECTION = cluster_style("#f7fbf8", "#c7d9ce")
VPC_SECTION = cluster_style("#f4fbf4", "#bfdcbf")
OPS_SECTION = cluster_style("#f9fafb", "#d1d5db")
SUBNET_SECTION = cluster_style("#fcfcff", "#d7d9ef")

CONFIG_EDGE = {"color": "#6b7280"}
PRIVATE_EDGE = {"color": "#218c4a", "penwidth": "2.3"}
MONITOR_EDGE = {"color": "#6b7280", "style": "dashed"}
IAM_EDGE = {"color": "#7c3aed"}


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    with Diagram(
        "Zero-Cost Secure Serverless Task Manager",
        filename=str(DOCS_DIR / "architecture"),
        outformat="png",
        show=False,
        direction="LR",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        browser = User("Browser")

        with Cluster("AWS Cloud", graph_attr=AWS_CLOUD):
            with Cluster("Frontend", graph_attr=SECTION):
                cloudfront = Custom("CloudFront", ICONS["cloudfront"])
                s3 = Custom("Private S3 Bucket\nOAC origin only", ICONS["s3"])

            with Cluster("IAM", graph_attr=SECTION):
                task_role = Custom("LambdaTaskRole\nDynamoDB + logs + ENI", ICONS["iam_role"])
                base_role = Custom("LambdaBaseRole\nlogs + ENI only", ICONS["iam_role"])

            with Cluster("API", graph_attr=SECTION):
                api = Custom("API Gateway\nCORS: https://<cf-domain>", ICONS["apigw"])
                fn = Custom("Lambda Task API\nPython CRUD", ICONS["lambda"])

            with Cluster("VPC\n10.0.0.0/16", graph_attr=VPC_SECTION):
                vpc_cfg = Custom("Custom VpcConfig\nSubnetIds + SG", ICONS["vpc"])
                lambda_sg = Blank("Lambda SG\n443 -> DynamoDB PL")

                with Cluster("AZ-a", graph_attr=SUBNET_SECTION):
                    subnet_a = Custom("Private Subnet A\n10.0.1.0/24", ICONS["subnet"])

                with Cluster("AZ-b", graph_attr=SUBNET_SECTION):
                    subnet_b = Custom("Private Subnet B\n10.0.2.0/24", ICONS["subnet"])

                route_table = Custom(
                    "Private Route Table\npl-xxxx -> vpce-xxxx",
                    ICONS["router"],
                )
                no_nat = Blank("No NAT Gateway")
                vpce = Custom("Gateway VPCE\nDynamoDB", ICONS["vpce"])

            ddb = Custom("DynamoDB\nTasks", ICONS["dynamodb"])

            with Cluster("Ops", graph_attr=OPS_SECTION):
                cloudwatch = Custom("CloudWatch\nlogs + alarms", ICONS["cloudwatch"])
                sns = Custom("SNS\nemail", ICONS["sns"])
                budgets = Custom("AWS Budgets\ncost alert", ICONS["budgets"])

        browser >> Edge(label="HTTPS", **CONFIG_EDGE) >> cloudfront
        cloudfront >> Edge(label="OAC", **CONFIG_EDGE) >> s3

        browser >> Edge(label="HTTPS", **CONFIG_EDGE) >> api
        api >> Edge(label="invoke", **CONFIG_EDGE) >> fn

        task_role >> Edge(label="task role", constraint="false", **IAM_EDGE) >> fn
        base_role

        fn >> Edge(label="VpcConfig", **CONFIG_EDGE) >> vpc_cfg
        vpc_cfg >> Edge(label="subnet", **CONFIG_EDGE) >> subnet_a
        vpc_cfg >> Edge(label="subnet", **CONFIG_EDGE) >> subnet_b
        vpc_cfg >> Edge(label="sg", **CONFIG_EDGE) >> lambda_sg
        subnet_a >> Edge(label="assoc", **CONFIG_EDGE) >> route_table
        subnet_b >> Edge(label="assoc", **CONFIG_EDGE) >> route_table

        lambda_sg >> Edge(label="443", **PRIVATE_EDGE) >> vpce
        route_table >> Edge(label="private", **PRIVATE_EDGE) >> vpce
        vpce >> Edge(label="private", **PRIVATE_EDGE) >> ddb

        fn >> Edge(label="logs", constraint="false", **MONITOR_EDGE) >> cloudwatch
        api >> Edge(label="metrics", constraint="false", **MONITOR_EDGE) >> cloudwatch
        cloudwatch >> Edge(label="alarm", constraint="false", **MONITOR_EDGE) >> sns
        budgets >> Edge(label="budget", constraint="false", **MONITOR_EDGE) >> sns

        cloudfront >> Edge(style="invis") >> api
        cloudfront >> Edge(style="invis") >> task_role
        task_role >> Edge(style="invis") >> api
        api >> Edge(style="invis") >> fn
        fn >> Edge(style="invis") >> vpc_cfg
        subnet_a >> Edge(style="invis") >> subnet_b
        subnet_b >> Edge(style="invis") >> route_table
        route_table >> Edge(style="invis") >> vpce
        vpce >> Edge(style="invis") >> ddb
        ddb >> Edge(style="invis") >> cloudwatch
        cloudwatch >> Edge(style="invis") >> sns
        sns >> Edge(style="invis") >> budgets
        route_table >> Edge(style="invis") >> no_nat

    print("[ok] generated docs/architecture.png")


if __name__ == "__main__":
    main()
