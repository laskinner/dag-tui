# DagTUI

![image](https://github.com/laskinner/dag-tui/assets/1858258/f85bc6d4-4ef0-47f5-ad89-cd5e89c765d0)

Link to live deployment: https://dag-tui-a0cf3a32c1bb.herokuapp.com/

## Overview
At the heart of this project lies the concept of a Directed Acyclic Graph (DAG), a graph to illustrate causal relationships between nodes. While DAGs can be highly complex visualizations, to limit the scope of this project, the purpose of this is to allow a user to create very simple, linear causal graphs which calculate the conditional probability of an outcome and its composite severity, using the data provided by its preceding causes.

The DAG is a unique type of graph that embodies three key characteristics:

- Directed: Each edge in the graph has a direction, indicating a specific flow from one node to another. This directionality is crucial as it defines the relationship between nodes, often signifying a sequence or a dependency from one node (the cause) to another (the outcome).

- Acyclic: The graph is devoid of cycles. This means there are no paths where a sequence of directed edges allows you to return to the starting node. The absence of cycles in the graph ensures that it can represent scenarios where backtracking is not feasible, such as time-based events or hierarchical structures.

- Graph: At its core, a DAG is a collection of nodes connected by edges. Each node typically represents an entity or an event, while the edges signify the relationships or interactions between these entities. The graphical nature of a DAG makes it an intuitive tool for visualizing complex relationships in a system.

The DAG TUI (Terminal User Interface) project leverages the structure of DAGs to offer users a practical tool for creating, managing, and visualizing their own directed acyclic graphs directly in the terminal.

## Features

### Existing Features

#### View Graph (Verbose)
- Users can view a detailed representation of the entire graph.
- This view includes each node's ID, title, description, relationships, probabilities, and severities, along with similar details for outcomes.
- Ideal for users who need a comprehensive understanding of the graph's structure.

#### View Graph (Visual)
- A simplified visual representation of the graph is provided.
- This view focuses on the relationships between nodes (causes) and outcomes, presented in a clear, linear format.
- Color coding for probabilities enhances the visual experience, helping users quickly gauge the likelihood of different outcomes.

#### Edit Nodes
- Users can select and edit any node in the graph.
- The editing interface allows changes to a node's title, description, relationships, probability, and severity.
- Ensures that the graph can be kept up-to-date and reflects the current understanding of relationships and dependencies.

#### Add Nodes
- The application provides an interface to add new nodes to the graph.
- Users can input the node's title, description, and its relationships (causes and causedBy).
- Automatically generates unique IDs for each new node to simplify tracking and editing.

#### Add Outcomes
- Similar to adding nodes, users can also add outcomes to the graph.
- Inputs include the outcome's title, description, and the nodes that cause it.
- Each outcome is given a unique ID and can be linked to multiple nodes.

#### Delete Nodes
- Users have the option to delete nodes from the graph.
- Ensures the graph remains relevant and uncluttered, especially in complex projects where dependencies may change over time.

#### Exit
- A simple and straightforward option to exit the application.
- Ensures a smooth end to the user session without leaving any processes hanging.

### Features Left to Implement

- **Graph Export Functionality:** Future versions could include the ability to export the graph in various formats for use in presentations or reports.
- **Interactive Graph Manipulation:** Allowing users to interactively rearrange and edit nodes directly within the graphical view.


## Testing

This section outlines the testing approach employed to ensure the Directed Acyclic Graph Tool (DagTUI) functions correctly and meets the project requirements.

### Functional Testing

Functional testing focused on verifying each feature of DagTUI:

1. **Node and Outcome Management:**
   - **Adding Nodes:** Tested the ability to add nodes with all required details.
   - **Editing Nodes:** Checked the functionality for updating node details, including outcomes.
   - **Deleting Nodes:** Ensured nodes could be removed from the graph.
   - **Adding Outcomes:** Verified the addition of outcomes and their connection to causes.
   - **Displaying Nodes and Outcomes:** Confirmed correct display in both verbose and simplified graph views.

2. **Graph Visualization:**
   - **Verbose View:** Validated detailed display of nodes and outcomes.
   - **Simplified Graphical View:** Checked for accurate and clear graphical representation.

3. **Automatic ID Generation:**
   - Ensured unique IDs were assigned upon node and outcome creation.

4. **Probability and Severity Calculations:**
   - Tested the logic for updating probabilities and severities of outcomes.

### Usability Testing

As the sole tester, I focused on ensuring the tool was intuitive and user-friendly. I assessed the interface, instructions clarity, and overall usability, making adjustments based on personal observations. There were too many adjustments to list here. However, examples include:
- Adjusting spacing between menus, headers, and text lines to improve readibility.
- Shortening the randomnly genereted IDs from ~10 digits to 4 digits. Entering long IDs when selecting nodes in menus was very cumbersome for a user. With more time, I would have simply hidden the IDs entirely from the UI, and allowed the user to select nodes using menu numbers. However, a much faster, simpler, and less error-prone solution was to simply adjust the ID generator method to generate shorter IDs.
- Adjusting column widths in tables to accommodate data while not exceeding 80 total characters in width.

### Error Handling and Data Validation

- Checked the application's response to invalid user inputs.
- Ensured appropriate error messages were displayed for incorrect actions.

### Cross-Platform Testing

No cross-platfrom testing was conducting, as DagTUI runs in a contained, browser-based environment.

### Known Bugs

- **Display Glitch while displaying nodes in table form:** There's an occasional minor misalignment in tables which display nodes, if node title exceeds a certain length.
- **Handling Large Graphs:** The current version does not optimally handle very large graphs in performance and display, primarily due to the fact this this is a terminal environment, and these kinds of projects are generally paired with a powerful GUI.

### Future Testing Plans

- Further testing edge scenarios around causal relationships should be conducted.

This testing documentation reflects my efforts as an individual developer to ensure the functionality and reliability of DagTUI. Future versions of the tool will incorporate more extensive testing methods for enhanced robustness.


### Validator Testing

CI Python Linter shows no issues:
![image](https://github.com/laskinner/dag-tui/assets/1858258/9d46a5a3-1e6a-4326-a163-0c673e168ac4)


### Unfixed Bugs

## Deployment
Automatic deployment is set up on Heroku.

Therefore, to deploy, simply create a pull request for me to review. When I review it, I'll merge and the deploy will be complete.

## Credits
Three libraries were used:

- Google spreadsheets
- time
- random

The 'time' and 'random' and libraries were used to generate the random IDs when creating nodes.


### Media
No external media was used in DagTUI.


## Reminders

* Your code must be placed in the `run.py` file
* Your dependencies must be placed in the `requirements.txt` file
* Do not edit any of the other files or your code may not deploy properly

## Creating the Heroku app

When you create the app, you will need to add two buildpacks from the _Settings_ tab. The ordering is as follows:

1. `heroku/python`
2. `heroku/nodejs`

You must then create a _Config Var_ called `PORT`. Set this to `8000`

If you have credentials, such as in the Love Sandwiches project, you must create another _Config Var_ called `CREDS` and paste the JSON into the value field.

Connect your GitHub repository and deploy as normal.

## Constraints

The deployment terminal is set to 80 columns by 24 rows. That means that each line of text needs to be 80 characters or less otherwise it will be wrapped onto a second line.

-----
Happy coding!
