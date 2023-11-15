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
        """
        Dictionaries for nodes, as well as their attributes, and edges 
        """
        self.nodes = {}
        self.edges = {}

    def add_node(self, node_id, **attributes):
        if node_id in self.nodes:
            print(f"Node {node_id} already exists.")
        else:
            self.nodes[node_id] = attributes
            self.edges[node_id] = []

    def add_edge(self, causedBy, causes):
        if causedBy in self.edges and causes in self.nodes:
            if causes not in self.edges[causedBy]:
                self.edges[causedBy].append(causes)
            else:
                print(f"Edge from {causedBy} to {causees} already exists.")
        else:
            print(f"One or both nodes do not exist: {causedBy}, {causes}")

    def visualize(self):
        for node in self.nodes:
            print(f"Node {node}: {self.nodes[node]['title']}")
            for edge in self.edges[node]:
                print(f"  -> {edge}")
            print()

# Example usage:
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
