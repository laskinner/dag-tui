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

    def add_edge(self, from_node, to_node):
        if from_node in self.edges and to_node in self.nodes:
            if to_node not in self.edges[from_node]:
                self.edges[from_node].append(to_node)
            else:
                print(f"Edge from {from_node} to {to_node} already exists.")
        else:
            print(f"One or both nodes do not exist: {from_node}, {to_node}")

    def visualize(self):
        for node in self.nodes:
            print(f"Node {node}: {self.nodes[node]['title']}")
            for edge in self.edges[node]:
                print(f"  -> {edge}")
            print()

# Example usage:
def main():
    print("Welcome to DagTui -- A Terminal User Interface for Directed Acyclic Graphs")
    dag = DAG()
    dag.add_node('node1', title='Node 1 Title', description='This is the description for node 1')
    dag.add_node('node2', title='Node 2 Title', description='This is the description for node 2')
    dag.add_edge('node1', 'node2')
    dag.add_edge('node1', 'node3')

    dag.visualize()

main()
