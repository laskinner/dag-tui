import gspread
from google.oauth2.service_account import Credentials
from pprint import pprint

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("dag-tui")

class DAG:
    def __init__(self):
        self.nodes_sheet = SHEET.worksheet('nodes')
        self.edges_sheet = SHEET.worksheet('edges')

    def add_node(self, node_id, **attributes):
        # Fetch data from the nodes worksheet
        node_data = self.nodes_sheet.get_all_values()

        # Check if node already exists (ignoring the header row)
        if any(node[0] == node_id for node in node_data[1:]):
            print(f"Node {node_id} already exists.")
            return

        # Add node to the nodes sheet
        self.nodes_sheet.append_row([node_id, attributes.get('title', ''), attributes.get('description', '')])

    def add_edge(self, causedBy, causes):
        # Fetch data from the edges worksheet
        edge_data = self.edges_sheet.get_all_values()

        # Check if edge already exists (ignoring the header row)
        if any(edge[1] == causedBy and edge[2] == causes for edge in edge_data[1:]):
            print(f"Edge from {causedBy} to {causes} already exists.")
            return

        # Add edge to the edges sheet
        self.edges_sheet.append_row([f'{causedBy}-{causes}', causedBy, causes])

def visualize(self):
    # Check if the nodes worksheet is empty
    if not self.nodes_sheet.get_all_values():
        print("No nodes to visualize.")
        return

    # Check if the edges worksheet is empty
    if not self.edges_sheet.get_all_values():
        print("No edges to visualize.")
        return

    # Read nodes and edges from sheets
    nodes = self.nodes_sheet.get_all_records()
    edges = self.edges_sheet.get_all_records()

    for node in nodes:
        print(f"Node {node['node_id']} - {node['title']}")
        print(f"  Description: {node['description']}")
        has_edges = False

        for edge in edges:
            if edge['causedBy'] == node['node_id']:
                print(f"    -> Causes: {edge['causes']}")
                has_edges = True

        if not has_edges:
            print("    [No outgoing edges]")

        print()

    # Identify and display orphan nodes
    print("Orphaned nodes:")
    orphan_nodes = [node for node in nodes if not any(edge['causedBy'] == node['node_id'] or edge['causes'] == node['node_id'] for edge in edges)]
    if orphan_nodes:
        for orphan in orphan_nodes:
            print(f"{orphan['node_id']} - {orphan['title']}: {orphan['description']}")
    else:
        print("All nodes are currently associated in graph.")

    print()

def main():
    print()
    print("Welcome to DagTui -- A Terminal User Interface for Directed Acyclic Graphs\n")
    dag = DAG()
    dag.add_node('4', title='Node 4', description='This is the description for node 4')
    dag.add_edge('4', '3')

    dag.visualize()

main()
