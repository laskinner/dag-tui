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
    # Class constants for colors
    GREEN = '\033[92m'  # Green text
    YELLOW = '\033[93m'  # Yellow text
    RED = '\033[91m'  # Red text
    RESET = '\033[0m'  # Reset to default text color

    def __init__(self):
        """Initialize with worksheets for nodes."""
        self.nodes_sheet = SHEET.worksheet('nodes')
        self.outcomes_sheet = SHEET.worksheet('outcomes')

    def generate_unique_id(self):
        """Generate a unique ID for nods and outcomes."""
        # Get the last two digits of the current timestamp
        timestamp = int(time.time()) % 100
        # Generate a random number between 10 and 99
        random_part = random.randint(10, 99)
        # Combine the two parts
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
        print(f"Probability: {node.get('probability', 'N/A')}%")
        print(f"Severity: {node.get('severity', 'N/A')}\n")

    def confirm_or_edit_node(self, node_id):
        """Ask the user to confirm or edit the node."""
        self.display_node(node_id)
        choice = input("Is this information correct? (yes/no): ").lower()
        if choice == 'no':
            self.edit_nodes(node_id)

    def add_node(self):
        """
        Interface for adding a new node to the DAG.
        """
        print("\nAdd New Cause\n")
        title = input("Enter Cause title: ")
        description = input("Enter Cause description: ")
        causedBy = input(
            "Enter Caused By (comma-separated IDs or leave blank): "
            )
        causes = input("Enter Causes (comma-separated IDs or leave blank): ")
        probability = input("Enter Probability (1-100 or leave blank): ")
        severity = input("Enter Severity (1-10 or leave blank): ")

        node_id = self.generate_unique_id()

        # Append new node data to the sheet
        self.nodes_sheet.append_row([
            node_id, title, description,
            causedBy or '', causes or '',
            probability or '', severity or ''
        ])

        # Update outcomes if the node causes any
        if causes:
            self.update_outcomes(causes, node_id)

        print(f"\nCause ID {node_id} added: {title}. "
              "\nPlease confirm the details:\n"
              )
        self.confirm_or_edit_node(node_id)

        # Updated probabilities and severities if necessary
        self.calculate_outcome_probabilities_and_severities()

    def update_outcomes(self, causes, node_id):
        """
        Update the outcomes caused by a node.
        """
        outcomes = self.outcomes_sheet.get_all_records()

        # Split the causes and iterate through each ID
        for outcome_id in causes.split(','):
            outcome_id = outcome_id.strip()
            if not outcome_id:
                continue

            for i, outcome in enumerate(outcomes, start=2):
                if str(outcome['outcome_id']).strip() == outcome_id:
                    current_causedBy = outcome.get('causedBy', '').strip()
                    updated_causedBy = (
                        f"{current_causedBy},{node_id}"
                        if current_causedBy else node_id
                    )

                    # Ensure proper separation
                    updated_causedBy = (
                        ', '.join(filter(None, updated_causedBy.split(',')))
                    )
                    self.outcomes_sheet.update(f'D{i}', [[updated_causedBy]])
                    print(
                        f"Updated causedBy for outcome ID {outcome_id} "
                        f"with node ID {node_id}"
                    )
                    break

    def visualize(self):
        """Visualize the DAG by printing nodes and their relationships."""
        if not self.nodes_sheet.get_all_values():
            print("No nodes to visualize.")
            return

        nodes = self.nodes_sheet.get_all_records()

        print("\n\nCauses:")

        for node in nodes:
            print(f"\nNode: {node['title']}")
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

        print("\nOutcomes:\n")
        outcomes = self.outcomes_sheet.get_all_records()
        if not outcomes:
            print("No outcomes to display.")
        else:
            for outcome in outcomes:
                self.display_outcome(str(outcome['outcome_id']))

    def update_node(self, node_id, title=None, description=None,
                    causedBy=None, causes=None, probability=None,
                    severity=None):
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

        # Update probabilities and severities if necessary
        self.calculate_outcome_probabilities_and_severities()

    def print_nodes(self):
        """Print nodes in a formatted table."""
        nodes = self.nodes_sheet.get_all_records()
        outcomes = self.outcomes_sheet.get_all_records()

        # Print header for nodes
        self.print_table_header("Causes")
        self.print_table_contents(nodes)

        # Print header for outcomes
        self.print_table_header("Outcomes")
        self.print_table_contents(outcomes, is_outcome=True)

    def print_table_header(self, header_title):
        """Prints the header for the table."""
        id_width = 5
        title_width = 15
        desc_width = 30
        caused_by_width = 15
        causes_width = 15
        total_width = (id_width + title_width + desc_width +
            caused_by_width + causes_width)

        print(f"\n{header_title}:")
        header = (f"{'ID':<{id_width}}"
                f"{'Title':<{title_width}}"
                f"{'Description':<{desc_width}}"
                f"{'Caused By (ID)':<{caused_by_width}}"
                f"{'Causes (ID)':<{causes_width}}")
        print(header)
        print('-' * total_width)

    def print_table_contents(self, items, is_outcome=False):
        """Prints the contents of the table."""
        for item in items:
            item_id = str(item['node_id'] if not is_outcome else item['outcome_id'])
            title = item['title']
            description = (
                item['description'][:27] + '...'
                if len(item['description']) > 27 else item['description']
            )
            caused_by = item.get('causedBy', 'N/A')
            causes = item.get('causes', 'N/A')

            if len(description) > 25:
                description = description[:20] + '...'

            print(
                f"{item_id:<5}"
                f"{title:<15}"
                f"{description:<30}"
                f"{caused_by:<15}"
                f"{causes:<15}"
            )

        if not items:
            print("No items to display.")

    def edit_nodes(self):
        """Interface for editing nodes."""
        self.print_nodes()
        node_id_to_edit = input(
                "\nEnter the ID of the node to edit (or 'exit'): ").strip()

        if node_id_to_edit.lower() == 'exit':
            return

        # Fetch all nodes and convert node_ids to string for comparison
        nodes = self.nodes_sheet.get_all_records()
        node_to_edit = next((node for node in nodes if str(node['node_id']) ==
                            node_id_to_edit), None)

        if not node_to_edit:
            print(f"No node found with ID {node_id_to_edit}")
            return

        print("Enter new values (leave blank to keep unchanged):")
        new_title = input(
            f"New Title [{node_to_edit.get('title', '')}]: "
        ) or node_to_edit['title']
        new_description = input(
            f"New Description [{node_to_edit.get('description', '')}]: "
        ) or node_to_edit['description']
        new_causedBy = input(
            f"New Caused By [{node_to_edit.get('causedBy', '')}]: "
        ) or node_to_edit.get('causedBy', '')
        new_causes = input(
            f"New Causes [{node_to_edit.get('causes', '')}]: "
        ) or node_to_edit.get('causes', '')
        new_probability = input(
            f"New Probability [{node_to_edit.get('probability', '')}]: "
        ) or node_to_edit.get('probability', '')
        new_severity = input(
            f"New Severity [{node_to_edit.get('severity', '')}]: "
        ) or node_to_edit.get('severity', '')

        self.update_node(node_id_to_edit, new_title, new_description,
                         new_causedBy, new_causes, new_probability,
                         new_severity)
        print(f"\nUpdated Node {node_id_to_edit}:")
        self.display_node(node_id_to_edit)

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

    def add_outcome(self):
        """Add a new outcome to the DAG."""
        print("\nAdd New Outcome\n")
        title = input("Enter outcome title: ")
        description = input("Enter outcome description: ")
        causedBy = input("Enter Caused By (comma-separated node IDs): ")
        probability = input("Enter Probability (1-100): ")
        severity = input("Enter Severity (1-10): ")

        outcome_id = self.generate_unique_id()

        self.outcomes_sheet.append_row([
            outcome_id, title, description, causedBy, probability, severity
        ])
        print(f"\nOutcome {title} added successfully.\n")

    def display_outcome(self, outcome_id):
        """Display a single outcome's details."""
        outcomes = self.outcomes_sheet.get_all_records()
        outcome = next((o for o in outcomes if str(o['outcome_id']) ==
                        str(outcome_id)), None)

        if not outcome:
            print(f"No outcome found with ID {outcome_id}")
            return

        print(f"Title: {outcome.get('title', 'N/A')}")
        print(f"  Description: {outcome.get('description', 'N/A')}")
        print(f"  Caused By: {outcome.get('causedBy', 'N/A')}")
        print(f"  Probability: {outcome.get('probability', 'N/A')}%")
        print(f"  Severity: {outcome.get('severity', 'N/A')}\n")

    def calculate_outcome_probabilities_and_severities(self):
        print("Calculating outcome probabilities and severities...\n")
        outcomes_sheet = SHEET.worksheet('outcomes')
        outcomes = outcomes_sheet.get_all_records()
        nodes = self.nodes_sheet.get_all_records()

        if not outcomes:
            print("No outcomes found.\n")
            return

        for i, outcome in enumerate(outcomes, start=2):
            # Split causedBy by comma and strip spaces
            causedBy_ids = [id.strip() for id in str(outcome.get(
                'causedBy', '')).split(',')]
            print(f"Processing outcome {outcome['title']} with causes...\n")
            total_probability, total_severity, count = 0, 0, 0

            for node_id in causedBy_ids:
                if node_id:  # Check if node_id is not empty
                    node = next((n for n in nodes if str(n['node_id']) ==
                                node_id), None)
                    if node:
                        node_probability = int(node.get('probability', 0))
                        node_severity = int(node.get('severity', 0))

                        total_probability += int(node.get('probability', 0))
                        total_severity = max(total_severity,
                                             int(node.get('severity', 0)))
                        count += 1
                        print(
                            f"Node ID {node_id} contributes with "
                            f"{node_probability}% probability and severity "
                            f"of {node_severity}"
                            )
                    else:
                        print(f"Node ID {node_id} not found in nodes")

            if count > 0:
                average_probability = total_probability / count
                outcomes_sheet.update(f'E{i}', [[average_probability]])
                outcomes_sheet.update(f'F{i}', [[total_severity]])

                print(f"Updating outcome ID {outcome['outcome_id']} with "
                      f"probability {average_probability} and severity "
                      f"{total_severity}\n")

        print("Outcome probabilities and severities updated.")

    def visualize_simple_graph(self):
        nodes = self.nodes_sheet.get_all_records()
        outcomes = self.outcomes_sheet.get_all_records()
        print("Simplified Graph View:")
        print("------------------------------------------------------")

        for node in nodes:
            node_title = node.get('title', 'N/A')
            node_probability = int(node.get('probability', 0))
            color = self.determine_color(node_probability)

            # Ensure causes is treated as a string
            causes_str = str(node.get('causes', ''))
            if causes_str:
                causes_list = causes_str.split(',')
                for cause in causes_list:
                    outcome = next((o for o in outcomes if
                                    str(o['outcome_id']) ==
                                    cause.strip()), None)
                    if outcome:
                        outcome_title = outcome.get('title', 'N/A')
                        outcome_probability = int(
                            outcome.get('probability', 0)
                        )
                        outcome_color = self.determine_color(
                            outcome_probability
                        )
                        print(f"{color}{node_title}{self.RESET} | ====> "
                              f"| {outcome_color}{outcome_title}{self.RESET}")
            print()

    def determine_color(self, probability):
        if probability < 30:
            return self.GREEN
        elif 30 <= probability <= 70:
            return self.YELLOW
        else:
            return self.RED


def main():
    print("\nWelcome to DagTui - A Terminal UI for Directed Acyclic Graphs\n")
    dag = DAG()
    while True:
        print("\nWhat would you like to do?\n")
        print("1. View graph (verbose view)")
        print("2. View graph (graphical view)")
        print("3. Edit nodes")
        print("4. Add nodes")
        print("5. Add outcomes")
        print("6. Delete nodes")
        print("7. Exit")

        try:
            choice = int(input("\nEnter your choice: "))
            if choice == 1:
                dag.visualize()
            if choice == 2:
                dag.visualize_simple_graph()
            elif choice == 3:
                dag.edit_nodes()
            elif choice == 4:
                dag.add_node()
            elif choice == 5:
                dag.add_outcome()
            elif choice == 6:
                dag.delete_node_ui()
            elif choice == 7:
                print("Exiting program.")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 5.")
        except ValueError:
            print("Please enter a valid number.")


if __name__ == "__main__":
    main()
