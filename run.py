import gspread
from google.oauth2.service_account import Credentials
import warnings
import time
import random

# Suppress specific deprecation warnings from Google Sheets API
warnings.filterwarnings(
    "ignore",
    message=(".*Method signature's arguments 'range_name' and 'values' "
             "will change their order.*")
)

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
    """Class to represent a Directed Acyclic Graph (DAG)
    and interact with Google Sheets.
    """

    def __init__(self):
        """Initialize with worksheets for nodes."""
        self.nodes_sheet = SHEET.worksheet('nodes')

    def generate_unique_id(self):
        """Generate a unique ID for nods and outcomes."""
        timestamp = int(time.time())
        random_part = random.randint(100, 999)
        return f"{timestamp}{random_part}"


    def display_node(self, node_id):
        """Display a single node's data."""
        nodes = self.nodes_sheet.get_all_records()
        node = next((n for n in nodes if str(n['node_id']) == node_id), None)

        if not node:
            print(f"No node found with ID {node_id}")
            return

        # Display the node's details
        print(f"\nNode ID: {node_id}")
        print(f"Title: {node.get('title', 'N/A')}")
        print(f"Description: {node.get('description', 'N/A')}")
        print(f"Caused By: {node.get('causedBy', 'N/A')}")
        print(f"Causes: {node.get('causes', 'N/A')}")
        print(f"Probability: {node.get('probability', 'N/A')}")
        print(f"Severity: {node.get('severity', 'N/A')}\n")

    def confirm_or_edit_node(self, node_id):
        """Ask the user to confirm or edit the node."""
        self.display_node(node_id)
        choice = input("Is this information correct? (yes/no): ").lower()
        if choice == 'no':
            self.edit_node_ui(node_id)

    def add_node(self, title, description, causedBy=None, causes=None,
                probability=None, severity=None):
        """
        Add a new node to the DAG.
        """
        node_id = self.generate_unique_id()
        node_data = self.nodes_sheet.get_all_values()

        if any(node[0] == node_id for node in node_data[1:]):
            print(f"Node {node_id} already exists.")
            return

        # Append new node data to the sheet
        self.nodes_sheet.append_row([
            node_id, title, description,
            causedBy or '', causes or '',
            probability or '', severity or ''
        ])
        print(f"Node {node_id} added. Please confirm the details:")
        self.confirm_or_edit_node(node_id)

    def visualize(self):
        """Visualize the DAG by printing nodes and their relationships."""
        if not self.nodes_sheet.get_all_values():
            print("No nodes to visualize.")
            return

        nodes = self.nodes_sheet.get_all_records()

        for node in nodes:
            print(f"Node {node['node_id']} - {node['title']}")
            print(f"  Description: {node['description']}")

            # Display the 'causedBy' relationships
            if node.get('causedBy'):
                print(f"  Caused By: {node['causedBy']}")
            else:
                print("  [No incoming edges]")

            # Display the 'causes' relationships
            if node.get('causes'):
                print(f"  Causes: {node['causes']}")
            else:
                print("  [No outgoing edges]")

            print()

    def update_node(self, node_id, title=None, description=None, 
                    causedBy=None, causes=None, probability=None, severity=None):
        """
        Update the details of a specific node.

        Args:
            node_id: Identifier of the node to update.
            title: (Optional) New title for the node.
            description: (Optional) New description for the node.
            causedBy: (Optional) Node IDs that cause this node.
            causes: (Optional) Node IDs that are caused by this node.
            probability: (Optional) Probability of the node.
            severity: (Optional) Severity of the node.
        """
        nodes = self.nodes_sheet.get_all_records()
        row_index = next(
            (i for i, node in enumerate(nodes, start=2)
            if str(node['node_id']) == str(node_id)), None)

        if not row_index:
            print(f"No node found with ID {node_id}")
            return

        # Update each attribute if it's provided
        if title is not None:
            self.nodes_sheet.update(f'B{row_index}', [[title]])
        if description is not None:
            self.nodes_sheet.update(f'C{row_index}', [[description]])
        if causedBy is not None:
            self.nodes_sheet.update(f'D{row_index}', [[causedBy]])
        if causes is not None:
            self.nodes_sheet.update(f'E{row_index}', [[causes]])
        if probability is not None:
            self.nodes_sheet.update(f'F{row_index}', [[probability]])
        if severity is not None:
            self.nodes_sheet.update(f'G{row_index}', [[severity]])

        print(f"Node {node_id} updated successfully.")

    def print_nodes(self):
        """Print nodes in a formatted table."""
        nodes = self.nodes_sheet.get_all_records()

        id_width = 10
        title_width = 20
        desc_width = 35
        caused_by_width = 20
        causes_width = 20
        total_width = id_width + title_width + desc_width + caused_by_width + \
            causes_width

        header = (f"{'ID':<{id_width}}"
                f"{'Title':<{title_width}}"
                f"{'Description':<{desc_width}}"
                f"{'Caused By (ID)':<{caused_by_width}}"
                f"{'Causes (ID)':<{causes_width}}")

        print("\nNodes:")
        print(header)
        print('-' * total_width)

        for node in nodes:
            node_id = str(node['node_id'])
            title = node['title']
            description = (node['description'][:27] + '...') \
                if len(node['description']) > 27 else node['description']
            caused_by = node.get('causedBy', 'N/A')
            causes = node.get('causes', 'N/A')

            if len(description) > 30:
                description = description[:25] + '... '

            print(
                f"{node_id:<{id_width}}"
                f"{title:<{title_width}}"
                f"{description:<{desc_width}}"
                f"{caused_by:<{caused_by_width}}"
                f"{causes:<{causes_width}}"
            )

        # Identify and display orphan nodes
        print("Orphaned nodes:")
        orphan_nodes = [n for n in nodes if not n.get('causedBy') and not n.get('causes')]
        if orphan_nodes:
            for orphan in orphan_nodes:
                print(f"{orphan['node_id']} - {orphan['title']}: {orphan['description']}")
        else:
            print("All nodes are currently associated in graph.")
        print()

    def edit_nodes(self):
        """Interface for editing nodes."""
        self.print_nodes()
        node_id_to_edit = input("\nEnter the ID of the node to edit (or 'exit'): ").strip()

        if node_id_to_edit.lower() == 'exit':
            return

        # Fetch all nodes and convert node_ids to string for comparison
        nodes = self.nodes_sheet.get_all_records()
        node_to_edit = next((node for node in nodes if str(node['node_id']) == node_id_to_edit), None)

        if not node_to_edit:
            print(f"No node found with ID {node_id_to_edit}")
            return

        print("Enter new values (leave blank to keep unchanged):")
        new_title = input(f"New Title [{node_to_edit.get('title', '')}]: ") or node_to_edit['title']
        new_description = input(f"New Description [{node_to_edit.get('description', '')}]: ") or node_to_edit['description']
        new_causedBy = input(f"New Caused By [{node_to_edit.get('causedBy', '')}]: ") or node_to_edit.get('causedBy', '')
        new_causes = input(f"New Causes [{node_to_edit.get('causes', '')}]: ") or node_to_edit.get('causes', '')
        new_probability = input(f"New Probability [{node_to_edit.get('probability', '')}]: ") or node_to_edit.get('probability', '')
        new_severity = input(f"New Severity [{node_to_edit.get('severity', '')}]: ") or node_to_edit.get('severity', '')

        self.update_node(node_id_to_edit, new_title, new_description, new_causedBy, new_causes, new_probability, new_severity)
        print(f"\nUpdated Node {node_id_to_edit}:")
        self.display_node(node_id_to_edit)

    def add_node_ui(self):
        """Interface for adding a new node."""
        print("\nAdd New Node")
        node_id = input("Enter node ID: ")
        title = input("Enter node title: ")
        description = input("Enter node description: ")

        self.add_node(node_id, title=title, description=description)
        print(f"Node {node_id} added successfully.")

    def delete_node(self, node_id):
        """Delete a node from the DAG."""
        nodes = self.nodes_sheet.get_all_records()
        row_index = next(
            (i for i, node in enumerate(nodes, start=2)
             if str(node['node_id']) == str(node_id)), None)

        if not row_index:
            print(f"No node found with ID {node_id}")
            return

        self.nodes_sheet.delete_rows(row_index)
        print(f"Node {node_id} deleted successfully.")

    def delete_node_ui(self):
        """Interface for deleting a node."""
        self.print_nodes()
        node_id = input("\nEnter the ID of the node to delete (or 'exit'): ")
        if node_id.lower() == 'exit':
            return

        self.delete_node(node_id)


def main():
    print("\nWelcome to DagTui - A Terminal UI for Directed Acyclic Graphs\n")
    dag = DAG()
    while True:
        print("\nWhat would you like to do?")
        print("1. View graph (default view)")
        print("2. Edit nodes")
        print("3. Add nodes")
        print("4. Delete nodes")
        print("5. Exit")

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
