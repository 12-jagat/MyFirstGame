



# Sliding Puzzle Solver - By Jagat Naraian Pathak

This is a 3x3 sliding puzzle game with an A* algorithm solver, built using Streamlit. The goal of the puzzle is to arrange the tiles in the correct order starting from a shuffled state. The game provides an interactive UI where players can solve the puzzle manually or let the program solve it using the A* search algorithm.

## Features:
- **Interactive Puzzle**: Click tiles to swap adjacent tiles and manually solve the puzzle.
- **A* Solver**: Use the A* algorithm to automatically solve the puzzle and display the solution path.
- **Game Info**: Displays the number of moves made, elapsed time, and current puzzle configuration.
- **Solution Path**: Shows the sequence of moves made during the A* solving process, both as a list and in a readable string format.
- **Timer**: Tracks the time taken to solve the puzzle manually or automatically.

## How to Run the Application

1. Clone the repository:
   ```bash
   git clone https://github.com/12-jagat/MyFirstGame
   cd sliding-puzzle-solver
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

4. Open your browser and navigate to the displayed local URL (usually `http://localhost:8501`).

## How the Game Works:

### Manual Play:
- Click on the tiles to swap them with the adjacent blank space.
- The puzzle will update instantly after each move.

### Auto-Solve (A* Algorithm):
- Click the "Solve with A*" button to use the A* algorithm to solve the puzzle.
- The path taken by the algorithm to solve the puzzle will be displayed both as a list of moves and as a string in the sidebar.

### Game Info:
- The **elapsed time** and **moves made** are displayed in real-time.
- The puzzle state is automatically reset when the **Reset Game** button is clicked.

### Winning Condition:
- The game ends when the puzzle is solved (i.e., the numbers are arranged in the correct order).
- A success message is shown, including the number of moves and time taken.

## Technologies Used:
- **Streamlit**: For the interactive web interface.
- **Python**: The primary programming language.
- **A* Algorithm**: Used to automatically solve the puzzle.

## How the A* Algorithm Works:
- The A* algorithm uses the **Manhattan distance** heuristic to estimate the cost of the shortest path to the goal.
- It explores the puzzle's state space, moving tiles to reach the goal configuration while tracking the least costly path.
- The algorithm's path is displayed in the UI, along with the step-by-step moves taken to reach the solution.

## Example:
### Final Solution Path as String:
- The solution path is shown in a string format, e.g., `"(0, 1) -> (1, 1) -> (1, 2) -> ..."`, indicating the movement of tiles in each step.

## License:
This project is open-source and available under the MIT License.

---

