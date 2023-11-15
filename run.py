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
        # Check if the worksheet is empty
        if self.nodes_sheet.row_count < 2:
            # The sheet is empty (no data rows)
            # Add the node directly
            self.nodes_sheet.append_row([node_id, attributes.get('title', ''), attributes.get('description', '')])
            return

        # Rest of your code...

    def add_edge(self, causedBy, causes):
        # Similar check for edges sheet
        if self.edges_sheet.row_count < 2:
            # The sheet is empty
            self.edges_sheet.append_row([f'{causedBy}-{causes}', causedBy, causes])
            return

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
            print(f"Node {node['id']}: {node['title']}")
            for edge in edges:
                if edge['causedBy'] == node['id']:
                    print(f"  -> {edge['causes']}")
            print()

def main():
    print()
    print("Welcome to DagTui -- A Terminal User Interface for Directed Acyclic Graphs\n")
    dag = DAG()
    dag.add_node('node1', title='Node 1', description='This is the description for node 1')
    dag.add_node('node2', title='Node 2', description='This is the description for node 2')
    dag.add_node('node3', title='Node 3', description='This is the description for node 3')
    dag.add_edge('node1', 'node2')
    dag.add_edge('node1', 'node3')

    dag.visualize()

main()
