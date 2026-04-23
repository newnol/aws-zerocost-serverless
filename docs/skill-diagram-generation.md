# Skill: Generate Beautiful AWS Architecture Diagrams

## Overview
This skill teaches how to create clean, professional AWS architecture diagrams using Python's `diagrams` library with custom AWS icons.

## Prerequisites
- Python 3.8+
- `diagrams` library installed
- AWS Architecture Icons package downloaded

## Setup

### 1. Install diagrams library
```bash
python -m venv .venv-diagrams
source .venv-diagrams/bin/activate  # On Windows: .venv-diagrams\Scripts\activate
pip install diagrams
```

### 2. Download AWS Icons
Download the official AWS Architecture Icons from:
https://aws.amazon.com/architecture/icons/

Extract to your project root with a folder structure like:
```
Icon-package_XXXXXXXX/
├── Architecture-Service-Icons_XXXXXXXX/
├── Architecture-Group-Icons_XXXXXXXX/
├── Resource-Icons_XXXXXXXX/
└── Category-Icons_XXXXXXXX/
```

## Key Principles for Beautiful Diagrams

### 1. Layout Direction
- **Horizontal (LR)**: Best for showing data flow from user to database
- **Vertical (TB)**: Best for showing layered architectures
- Choose based on your narrative

### 2. Color Scheme
Use distinct, professional colors for each layer:
```python
# Pastel backgrounds with darker borders
FRONTEND_CLUSTER = cluster_style("#FFF3E0", "#E65100", "#BF360C")  # Orange
API_CLUSTER = cluster_style("#F3E5F5", "#6A1B9A", "#4A148C")       # Purple
VPC_CLUSTER = cluster_style("#E8F5E9", "#2E7D32", "#1B5E20")       # Green
MONITORING_CLUSTER = cluster_style("#FCE4EC", "#C2185B", "#880E4F") # Pink
```

### 3. Edge Styling
Differentiate edge types with colors and styles:
```python
# Data flow edges
data_edge = {"color": "#7B1FA2", "penwidth": "2.5"}

# Private network edges
private_edge = {"color": "#00C853", "penwidth": "3.0"}

# Monitoring/logging edges
monitor_edge = {"color": "#D81B60", "style": "dashed"}

# IAM/permission edges
iam_edge = {"color": "#9C27B0", "style": "dashed"}
```

### 4. Graph Attributes
```python
GRAPH_ATTR = {
    "fontname": "Arial",           # Clean, professional font
    "fontsize": "24",              # Large title
    "labelloc": "t",               # Title at top
    "pad": "0.8",                  # Padding around diagram
    "ranksep": "2.0",              # Space between ranks (horizontal)
    "nodesep": "1.5",              # Space between nodes
    "splines": "spline",           # Smooth curved edges
    "bgcolor": "#ffffff",          # White background
}
```

### 5. Node Attributes
```python
NODE_ATTR = {
    "fontname": "Arial",
    "fontsize": "13",              # Readable size
    "margin": "0.3",               # Space around text
    "shape": "box",
    "style": "rounded",            # Rounded corners
}
```

### 6. Cluster Styling
```python
def cluster_style(bg: str, border: str, label_color: str = "#000000") -> dict[str, str]:
    return {
        "bgcolor": bg,             # Light background
        "pencolor": border,        # Darker border
        "fontcolor": label_color,  # Dark text
        "fontsize": "18",          # Cluster title size
        "labeljust": "l",          # Left-align label
        "margin": "30",            # Internal padding
        "penwidth": "2.5",         # Thick border
        "style": "rounded,filled", # Rounded + filled
    }
```

## Template Structure

```python
from pathlib import Path
from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.client import User

# 1. Setup paths
REPO_ROOT = Path(__file__).resolve().parents[1]
ICON_BASE = REPO_ROOT / "Icon-package_XXXXXXXX"

# 2. Icon helper function
def icon(*parts: str) -> str:
    path = ICON_BASE.joinpath(*parts)
    if not path.exists():
        raise FileNotFoundError(path)
    return str(path)

# 3. Define icon mappings
ICONS = {
    "service_name": icon(
        "Architecture-Service-Icons_XXXXXXXX",
        "Arch_Category",
        "48",
        "Arch_Service-Name_48.png",
    ),
}

# 4. Define styling
GRAPH_ATTR = {...}
NODE_ATTR = {...}
EDGE_ATTR = {...}

# 5. Create diagram
def main():
    with Diagram(
        "Your Architecture Title",
        filename="output_path",
        outformat="png",
        show=False,
        direction="LR",  # or "TB"
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        # Define components
        user = User("User")
        
        with Cluster("AWS Cloud", graph_attr=AWS_CLOUD):
            with Cluster("Layer 1", graph_attr=LAYER1_STYLE):
                component1 = Custom("Component 1", ICONS["icon1"])
            
            with Cluster("Layer 2", graph_attr=LAYER2_STYLE):
                component2 = Custom("Component 2", ICONS["icon2"])
        
        # Define connections
        user >> Edge(label="HTTPS", color="#FF6F00", penwidth="2.5") >> component1
        component1 >> Edge(label="Invoke", color="#7B1FA2", penwidth="2.5") >> component2

if __name__ == "__main__":
    main()
```

## Best Practices

### 1. Label Conciseness
Keep labels short and informative:
- ✅ "CloudFront\nCDN"
- ✅ "Lambda\nPython 3.12"
- ❌ "CloudFront Content Delivery Network with caching enabled"

### 2. Logical Grouping
Group related components in clusters:
- Frontend Layer: CloudFront + S3
- API Layer: API Gateway + Lambda + IAM
- Network Layer: VPC + Subnets + Endpoints
- Monitoring: CloudWatch + SNS + Budgets

### 3. Visual Hierarchy
- Main data flow: Thick, solid, colored edges
- Configuration/association: Medium, dashed edges
- Monitoring/logging: Thin, dashed edges

### 4. Color Consistency
Use consistent colors for similar concepts:
- Orange/Red: Frontend, CDN, static content
- Purple: API, compute, serverless
- Green: Networking, VPC, private connections
- Pink/Red: Monitoring, alerts, operations
- Blue: Subnets, availability zones

### 5. Spacing
Adjust spacing for readability:
- `ranksep`: 1.5-2.5 for horizontal spacing
- `nodesep`: 1.0-1.5 for vertical spacing
- `margin`: 25-35 for cluster padding

## Common AWS Icon Paths

### Services (Architecture-Service-Icons)
```python
# Compute
"Arch_Compute/48/Arch_AWS-Lambda_48.png"

# Networking
"Arch_Networking-Content-Delivery/48/Arch_Amazon-API-Gateway_48.png"
"Arch_Networking-Content-Delivery/48/Arch_Amazon-CloudFront_48.png"

# Database
"Arch_Databases/48/Arch_Amazon-DynamoDB_48.png"

# Management
"Arch_Management-Tools/48/Arch_Amazon-CloudWatch_48.png"

# Integration
"Arch_Application-Integration/48/Arch_Amazon-Simple-Notification-Service_48.png"

# Cost
"Arch_Cloud-Financial-Management/48/Arch_AWS-Budgets_48.png"
```

### Resources (Resource-Icons)
```python
# Storage
"Res_Storage/Res_Amazon-Simple-Storage-Service_S3-Standard_48.png"

# Networking
"Res_Networking-Content-Delivery/Res_Amazon-VPC_Virtual-private-cloud-VPC_48.png"
"Res_Networking-Content-Delivery/Res_Amazon-VPC_Endpoints_48.png"
"Res_Networking-Content-Delivery/Res_Amazon-VPC_Router_48.png"

# Security
"Res_Security-Identity/Res_AWS-Identity-Access-Management_Role_48.png"
```

### Groups (Architecture-Group-Icons)
```python
"Private-subnet_32.png"
"Public-subnet_32.png"
"Availability-Zone_32.png"
```

## Troubleshooting

### Icons not found
- Check the icon package folder name matches your path
- Verify the icon file exists at the specified path
- Use `ls` to explore the icon directory structure

### Diagram looks cluttered
- Increase `ranksep` and `nodesep`
- Increase cluster `margin`
- Reduce number of components per cluster
- Split into multiple diagrams

### Edges overlap
- Change `splines` from "ortho" to "spline" or "curved"
- Adjust node positions with invisible edges
- Use `constraint="false"` on some edges

### Text too small/large
- Adjust `fontsize` in GRAPH_ATTR (title)
- Adjust `fontsize` in NODE_ATTR (node labels)
- Adjust `fontsize` in cluster_style (cluster titles)
- Adjust `fontsize` in EDGE_ATTR (edge labels)

## Example Output Characteristics

A well-designed diagram should have:
- ✅ Clear visual hierarchy
- ✅ Consistent color scheme
- ✅ Readable labels at normal zoom
- ✅ Logical left-to-right or top-to-bottom flow
- ✅ Distinct layers/sections
- ✅ Appropriate spacing (not too cramped)
- ✅ Professional appearance suitable for presentations

## Running the Script

```bash
# Activate virtual environment
source .venv-diagrams/bin/activate

# Run the script
python scripts/generate_diagram.py

# Output will be generated at specified location
# Example: docs/architecture.png
```

## Customization Tips

### For Different Project Types

**Microservices Architecture:**
- Use vertical layout (TB)
- Group services by domain
- Use different colors per service

**Data Pipeline:**
- Use horizontal layout (LR)
- Show data flow clearly
- Use arrows to indicate direction

**Multi-Region Setup:**
- Use nested clusters for regions
- Use different background colors per region
- Show cross-region connections clearly

**Security-Focused:**
- Highlight security boundaries with thick borders
- Use red/orange for public-facing components
- Use green for private/internal components
- Show IAM roles and policies explicitly

## References

- [Diagrams Documentation](https://diagrams.mingrammer.com/)
- [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/)
- [Graphviz Attributes](https://graphviz.org/doc/info/attrs.html)
