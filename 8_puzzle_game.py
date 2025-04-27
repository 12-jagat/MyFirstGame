import streamlit as st
import random
import copy
import time
import heapq

# --- Utility functions ---
def is_solvable(board, size):
    flat_board = sum(board, [])
    inv_count = sum(
        1
        for i in range(len(flat_board))
        for j in range(i + 1, len(flat_board))
        if flat_board[i] and flat_board[j] and flat_board[i] > flat_board[j]
    )
    if size % 2 == 1:
        return inv_count % 2 == 0
    else:
        blank_row = size - next(i for i in range(size) if 0 in board[i])
        return (inv_count + blank_row) % 2 == 0

def get_blank(board):
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 0:
                return i, j

def valid_moves(x, y, size):
    moves = []
    if x > 0: moves.append((x - 1, y))
    if x < size - 1: moves.append((x + 1, y))
    if y > 0: moves.append((x, y - 1))
    if y < size - 1: moves.append((x, y + 1))
    return moves

def create_board(size):
    board = list(range(size * size))
    while True:
        random.shuffle(board)
        board_2d = [board[i * size:(i + 1) * size] for i in range(size)]
        if is_solvable(board_2d, size):
            return board_2d

# --- A* Algorithm for Puzzle Solving ---
def manhattan_distance(board, size):
    dist = 0
    for i in range(size):
        for j in range(size):
            val = board[i][j]
            if val != 0:
                target_x, target_y = divmod(val - 1, size)
                dist += abs(i - target_x) + abs(j - target_y)
    return dist

def a_star(board, size):
    start = tuple(tuple(row) for row in board)
    goal = ((1, 2, 3), (4, 5, 6), (7, 8, 0))  # Goal state for 3x3 puzzle

    open_list = []
    heapq.heappush(open_list, (0 + manhattan_distance(board, size), 0, start, []))
    seen = set()
    seen.add(start)

    while open_list:
        _, g, current, path = heapq.heappop(open_list)
        if current == goal:
            return path

        x, y = get_blank(current)
        for nx, ny in valid_moves(x, y, size):
            new_board = [list(row) for row in current]
            new_board[x][y], new_board[nx][ny] = new_board[nx][ny], new_board[x][y]
            new_tuple = tuple(tuple(row) for row in new_board)

            if new_tuple not in seen:
                seen.add(new_tuple)
                heapq.heappush(open_list, (g + 1 + manhattan_distance(new_board, size), g + 1, new_tuple, path + [(x, y, nx, ny)]))
    return []

# --- Streamlit UI ---
st.set_page_config(page_title="Sliding Puzzle", layout="wide")

# --- Sidebar for login ---
with st.sidebar:
    st.title("Login")
    player_name = st.text_input("Enter your name:", key="login")
    size = st.selectbox("Select Puzzle Size:", (3,))  # Only 3x3

if not player_name:
    st.warning("Please enter your name to start!")
    st.stop()

# Initialize session state
if "board" not in st.session_state:
    st.session_state.board = create_board(size)
    st.session_state.start_time = time.time()
    st.session_state.moves = 0
    st.session_state.auto_solve_path = []
    st.session_state.start_board = copy.deepcopy(st.session_state.board)

board = st.session_state.board

st.title(f"Welcome {player_name}! Solve the 3x3 Puzzle 🎯")

col1, col2 = st.columns([2, 1])

# --- Main Puzzle Area ---
with col1:
    for i in range(size):
        cols = st.columns(size)
        for j in range(size):
            if board[i][j] != 0:
                if cols[j].button(str(board[i][j]), use_container_width=True, key=(i,j)):
                    x, y = get_blank(board)
                    if (i, j) in valid_moves(x, y, size):
                        board[x][y], board[i][j] = board[i][j], board[x][y]
                        st.session_state.moves += 1
                        st.rerun()  # Instantly update the UI after each move.

# --- Right Sidebar Info ---
with col2:
    st.subheader("Game Info")
    elapsed_time = int(time.time() - st.session_state.start_time)
    st.write(f"⏱️ Time Elapsed: {elapsed_time} seconds")
    st.write(f"🎮 Moves Made: {st.session_state.moves}")
    st.write(f"Puzzle Size: 3x3")

    if st.button("Solve with A*"):
        path = a_star(board, size)
        if path:
            st.session_state.auto_solve_path = path
            st.success("✅ Auto-solving started!")

    if st.button("Reset Game"):
        st.session_state.board = create_board(size)
        st.session_state.moves = 0
        st.session_state.start_time = time.time()
        st.session_state.auto_solve_path = []
        st.rerun()

    # Display the solution path in a presentable format
    if st.session_state.auto_solve_path:
        st.subheader("A* Solution Path:")
        moves_str = "\n".join([f"Move {i+1}: Move tile {board[x][y]} from ({x}, {y}) to ({nx}, {ny})" for i, (x, y, nx, ny) in enumerate(st.session_state.auto_solve_path)])
        st.text(moves_str)

        # Display final path as a string
        final_path_str = " -> ".join([f"({x}, {y}) -> ({nx}, {ny})" for (x, y, nx, ny) in st.session_state.auto_solve_path])
        st.subheader("Final Path (as String):")
        st.write(final_path_str)

st.divider()

# --- Game Win Condition ---
if sum(board, []) == list(range(1, size*size)) + [0]:
    elapsed_time = int(time.time() - st.session_state.start_time)
    st.balloons()
    st.success(f"🎉 Congratulations {player_name}! Solved in {st.session_state.moves} moves and {elapsed_time} seconds!")

# --- Animate Auto Solving ---
if st.session_state.auto_solve_path:
    # Pop the first move from the path
    move = st.session_state.auto_solve_path.pop(0)
    x, y, nx, ny = move
    board[x][y], board[nx][ny] = board[nx][ny], board[x][y]

    # Display the move
    st.write(f"Moving tile {board[nx][ny]} from ({x}, {y}) to ({nx}, {ny})")

    # Add a small delay for animation effect
    time.sleep(1)
    st.rerun()
