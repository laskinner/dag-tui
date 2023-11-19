# DagTUI

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

### Validator Testing

### Unfixed Bugs

## Deployment

## Credits

### Content

### Media



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
