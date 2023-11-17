import gspread
from google.oauth2.service_account import Credentials
from pprint import pprint
import warnings

# Suppress specific deprecation warnings from Google Sheets API regarding future proofing code
warnings.filterwarnings("ignore", message=".*Method signature's arguments 'range_name' and 'values' will change their order.*")

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
    """A class to represent a Directed Acyclic Graph (DAG) and interact with Google Sheets for data storage."""

    def __init__(self):
        """Initialize the DAG class with worksheets for nodes and edges."""
        self.nodes_sheet = SHEET.worksheet('nodes')
        self.edges_sheet = SHEET.worksheet('edges')

    def add_node(self, node_id, **attributes):
        """
        Add a new node to the DAG.

        Args:
            node_id: An identifier for the node.
            **attributes: Arbitrary keyword arguments representing node attributes, like title and description.
        """
        # Fetch data from the nodes worksheet
        node_data = self.nodes_sheet.get_all_values()

        # Check if node already exists (ignoring the header row)
        if any(node[0] == node_id for node in node_data[1:]):
            print(f"Node {node_id} already exists.")
            return

        # Add node to the nodes sheet
        self.nodes_sheet.append_row([node_id, attributes.get('title', ''), attributes.get('description', '')])

    def add_edge(self, causedBy, causes):
        """
        Add a new edge to the DAG.

        Args:
            causedBy: The node_id of the node causing the edge.
            causes: The node_id of the node that is caused by the edge.
        """
        # Fetch data from the edges worksheet
        edge_data = self.edges_sheet.get_all_values()

        # Check if edge already exists (ignoring the header row)
        if any(edge[1] == causedBy and edge[2] == causes for edge in edge_data[1:]):
            print(f"Edge from {causedBy} to {causes} already exists.")
            return

        # Add edge to the edges sheet
        self.edges_sheet.append_row([f'{str(causedBy)}-{str(causes)}', str(causedBy), str(causes)])

    def visualize(self):
        """
        Visualize the DAG by printing nodes and their relationships.
        """
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

    def update_node(self, node_id, title=None, description=None):
        """
        Update the details of a specific node.

        Args:
            node_id: The identifier of the node to update.
            title: (Optional) The new title for the node.
            description: (Optional) The new description for the node.
        """
        # Fetch all nodes
        nodes = self.nodes_sheet.get_all_records()
        # Find the row index of the node to update
        row_index = next((i for i, node in enumerate(nodes, start=2) if str(node['node_id']) == str(node_id)), None)

        if not row_index:
            print(f"No node found with ID {node_id}")
            return

        # Update the node's details
        if title is not None:
            self.nodes_sheet.update(range_name=f'B{row_index}', values=[[title]])
        if description is not None:
            self.nodes_sheet.update(range_name=f'C{row_index}', values=[[description]])
        print(f"Node {node_id} updated successfully.")

    def print_nodes(self):
        """
        Print the nodes in a formatted table.
        """
        nodes = self.nodes_sheet.get_all_records()
        edges = self.edges_sheet.get_all_records()
        
        # Define the width of each column
        id_width = 10
        title_width = 20
        desc_width = 35
        caused_by_width = 20
        causes_width = 20
        total_width = id_width + title_width + desc_width + caused_by_width + causes_width

        print("\nNodes:")
        print(f"{'ID':<{id_width}}{'Title':<{title_width}}{'Description':<{desc_width}}{'Caused By (ID)':<{caused_by_width}}{'Causes (ID)':<{causes_width}}")
        
        # Print the horizontal ruler
        print('-' * total_width)

        for node in nodes:
            node_id = str(node['node_id'])
            title = node['title']
            description = (node['description'][:27] + '...') if len(node['description']) > 27 else node['description']
            caused_by = ', '.join([str(edge['causedBy']) for edge in edges if str(edge['causes']) == node_id])
            causes = ', '.join([str(edge['causes']) for edge in edges if str(edge['causedBy']) == node_id])

            if len(description) > 30:
                description = description[:25] + '... '  # Truncate and add ellipsis

            print(f"{node_id:<{id_width}}{title:<{title_width}}{description:<{desc_width}}{caused_by:<{caused_by_width}}{causes:<{causes_width}}")

        # Identify and display orphan nodes
        print("Orphaned nodes:")
        orphan_nodes = [node for node in nodes if not any(edge['causedBy'] == node['node_id'] or edge['causes'] == node['node_id'] for edge in edges)]
        if orphan_nodes:
            for orphan in orphan_nodes:
                print(f"{orphan['node_id']} - {orphan['title']}: {orphan['description']}")
        else:
            print("All nodes are currently associated in graph.")

        print()

    def edit_nodes(self):
        """
        Provide an interface for editing nodes in the DAG.
        """
        self.print_nodes()

        node_id_to_edit = input("\nEnter the ID of the node you wish to edit (or 'exit' to go back): ")
        if node_id_to_edit.lower() == 'exit':
            return
        
        # Get new values for title and description
        new_title = input("Enter new title (or leave blank to keep unchanged): ")
        new_description = input("Enter new description (or leave blank to keep unchanged): ")

        # Call the update method
        self.update_node(node_id_to_edit, title=new_title if new_title else None, description=new_description if new_description else None)

    def add_node_ui(self):
        """
        Interface for adding a new node to the DAG.
        """
        print("\nAdd New Node")
        node_id = input("Enter node ID: ")
        title = input("Enter node title: ")
        description = input("Enter node description: ")

        # Call the add_node method
        self.add_node(node_id, title=title, description=description)
        print(f"Node {node_id} added successfully.")

    def delete_node(self, node_id):
        """
        Delete a node from the DAG.

        Args:
            node_id: The identifier of the node to delete.
        """
        nodes = self.nodes_sheet.get_all_records()
        row_index = next((i for i, node in enumerate(nodes, start=2) if str(node['node_id']) == str(node_id)), None)

        if not row_index:
            print(f"No node found with ID {node_id}")
            return

        # Delete the node
        self.nodes_sheet.delete_rows(row_index)
        print(f"Node {node_id} deleted successfully.")

    def delete_node_ui(self):
        """
        Interface for deleting a node from the DAG.
        """
        self.print_nodes()
        node_id = input("\nEnter the ID of the node you wish to delete (or 'exit' to go back): ")
        if node_id.lower() == 'exit':
            return

        self.delete_node(node_id)

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
                    dag.edit_nodes()
                elif choice == 3:
                    dag.add_node_ui()
                elif choice == 4:
                    dag.delete_node_ui()
                elif choice == 5:
                    print("Exiting program.")
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
if __name__ == "__main__":
    main()
