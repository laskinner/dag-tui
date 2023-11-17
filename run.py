import gspread
from google.oauth2.service_account import Credentials
import warnings

# Suppress specific deprecation warnings from Google Sheets API
warnings.filterwarnings(
    "ignore", 
    message=".*Method signature's arguments 'range_name' and 'values' will change their order.*"
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
        """Initialize with worksheets for nodes and edges."""
        self.nodes_sheet = SHEET.worksheet('nodes')
        self.edges_sheet = SHEET.worksheet('edges')

    def add_node(self, node_id, **attributes):
        """
        Add a new node to the DAG.

        Args:
            node_id: Identifier for the node.
            **attributes: Node attributes (title, description, etc.).
        """
        node_data = self.nodes_sheet.get_all_values()

        if any(node[0] == node_id for node in node_data[1:]):
            print(f"Node {node_id} already exists.")
            return

        self.nodes_sheet.append_row(
            [node_id, attributes.get('title', ''),
                attributes.get('description', '')]
        )

    def add_edge(self, causedBy, causes):
        """
        Add a new edge to the DAG.

        Args:
            causedBy: Node causing the edge.
            causes: Node caused by the edge.
        """
        edge_data = self.edges_sheet.get_all_values()

        if any(edge[1] == causedBy and edge[2]
                == causes for edge in edge_data[1:]):
            print(f"Edge from {causedBy} to {causes} already exists.")
        return

        self.edges_sheet.append_row(
            [f'{str(causedBy)}-{str(causes)}', str(causedBy), str(causes)]
        )

    def visualize(self):
        """Visualize the DAG by printing nodes and their relationships."""
        if not self.nodes_sheet.get_all_values():
            print("No nodes to visualize.")
            return

        if not self.edges_sheet.get_all_values():
            print("No edges to visualize.")
            return

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
            node_id: Identifier of the node to update.
            title: (Optional) New title for the node.
            description: (Optional) New description for the node.
        """
        nodes = self.nodes_sheet.get_all_records()
        row_index = next(
            (i for i, node in enumerate(nodes, start=2)
             if str(node['node_id']) == str(node_id)), None)

        if not row_index:
            print(f"No node found with ID {node_id}")
            return

        if title is not None:
            self.nodes_sheet.update(
                range_name=f'B{row_index}', values=[[title]])
        if description is not None:
            self.nodes_sheet.update(
                range_name=f'C{row_index}', values=[[description]])
        print(f"Node {node_id} updated successfully.")

    def print_nodes(self):
        """Print nodes in a formatted table."""
        nodes = self.nodes_sheet.get_all_records()
        edges = self.edges_sheet.get_all_records()

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

            caused_by_list = [
                str(edge['causedBy']) for edge in edges
                if str(edge['causes']) == node_id
            ]
            causes_list = [
                str(edge['causes']) for edge in edges
                if str(edge['causedBy']) == node_id
            ]

            caused_by = ', '.join(caused_by_list)
            causes = ', '.join(causes_list)

            if len(description) > 30:
                description = description[:25] + '... '

            print(
                f"{node_id:<{id_width}}"
                f"{title:<{title_width}}"
                f"{description:<{desc_width}}"
                f"{caused_by:<{caused_by_width}}"
                f"{causes:<{causes_width}}"
            )

        print("Orphaned nodes:")
        orphan_nodes = [node for node in nodes if not any(edge['causedBy'] ==
                        node['node_id'] or edge['causes'] == node['node_id']
            for edge in edges)]
        if orphan_nodes:
            for orphan in orphan_nodes:
                print(f"{orphan['node_id']} - {orphan['title']}: " +
                    f"{orphan['description']}")
        else:
            print("All nodes are currently associated in graph.")
        print()

    def edit_nodes(self):
        """Interface for editing nodes."""
        self.print_nodes()
        node_id_to_edit = input
        ("\nEnter the ID of the node to edit (or 'exit'): ")
        if node_id_to_edit.lower() == 'exit':
            return

        new_title = input
        ("Enter new title (or leave blank to keep unchanged): ")
        new_description = input
        ("Enter new description (or leave blank to keep unchanged): ")

        self.update_node(
            node_id_to_edit,
            title=new_title if new_title else None,
            description=new_description if new_description else None
        )

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
