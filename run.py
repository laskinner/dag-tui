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

    def edit_nodes(self):
        nodes = self.nodes_sheet.get_all_records()
        edges = self.edges_sheet.get_all_records()

        print("\nNodes:")
        print(f"{'ID':<10}{'Title':<20}{'Description':<30}{'Caused By':<20}{'Causes':<20}")
        for node in nodes:
            node_id = node['node_id']
            title = node['title']
            description = node['description']

            # Find edges related to this node
            caused_by = ', '.join([str(edge['causedBy']) for edge in edges if str(edge['causes']) == node_id])
            causes = ', '.join([str(edge['causes']) for edge in edges if str(edge['causedBy']) == node_id])

            print(f"{node_id:<10}{title:<20}{description:<30}{caused_by:<20}{causes:<20}")

        # Placeholder for further edit functionality
        print("\nEdit functionality to be implemented.")

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
    while True:
            # Print the menu
            print("\nWhat would you like to do?")
            print("1. View graph (default view)")
            print("2. Edit nodes")
            print("3. Add nodes")
            print("4. Delete nodes")
            print("5. Exit")

            # Get user input with validation
            try:
                choice = int(input("Enter your choice (1-5): "))

                if choice == 1:
                    dag.visualize()
                elif choice == 2:
                    # Placeholder for edit nodes functionality
                    dag.edit_nodes()
                elif choice == 3:
                    # Placeholder for add nodes functionality
                    print("Add nodes functionality not implemented yet.")
                elif choice == 4:
                    # Placeholder for delete nodes functionality
                    print("Delete nodes functionality not implemented yet.")
                elif choice == 5:
                    print("Exiting program.")
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
if __name__ == "__main__":
    main()
