import streamlit as st
import random
import copy
import time
import heapq

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
        .main {
            background: #f2f6fa;
            padding: 10px;
            font-family: 'Segoe UI', sans-serif;
        }
        button[kind="primary"] {
            background-color: #3498db !important;
            color: white !important;
            border-radius: 10px;
            font-size: 18px !important;
            padding: 10px !important;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .stButton>button {
            transition: 0.3s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #2980b9 !important;
            transform: scale(1.05);
        }
        .move-info {
            color: #2c3e50;
            font-weight: 500;
        }
        .compressed-path {
            font-family: monospace;
            color: #8e44ad;
            font-size: 15px;
            padding: 0.5em;
        }
        .tile {
            background-color: #ecf0f1;
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
        }
        .tile:hover {
            background-color: #bdc3c7;
        }
    </style>
""", unsafe_allow_html=True)

# --- Utility Functions ---
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
    goal = ((1, 2, 3), (4, 5, 6), (7, 8, 0))
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

# --- Streamlit Setup ---
st.set_page_config(page_title="Colorful Sliding Puzzle", layout="wide")

with st.sidebar:
    st.title("🎮 Login Panel")
    player_name = st.text_input("Enter your name")
    size = st.selectbox("Puzzle Size", [3])

if not player_name:
    st.warning("Enter your name to start the game!")
    st.stop()

if "board" not in st.session_state:
    st.session_state.board = create_board(size)
    st.session_state.start_time = time.time()
    st.session_state.moves = 0
    st.session_state.auto_solve_path = []

board = st.session_state.board

st.title(f"🎯 Sliding Puzzle - Welcome {player_name}!")

col1, col2 = st.columns([2, 1])

# --- Puzzle Grid ---
with col1:
    for i in range(size):
        cols = st.columns(size)
        for j in range(size):
            if board[i][j] != 0:
                if cols[j].button(f"{board[i][j]}", key=(i, j)):
                    x, y = get_blank(board)
                    if (i, j) in valid_moves(x, y, size):
                        board[x][y], board[i][j] = board[i][j], board[x][y]
                        st.session_state.moves += 1
                        st.rerun()
            else:
                cols[j].markdown("### ")

# --- Sidebar Info ---
with col2:
    st.subheader("📊 Game Info")
    st.write(f"🕒 Time Elapsed: `{int(time.time() - st.session_state.start_time)} sec`")
    st.write(f"🔁 Moves: `{st.session_state.moves}`")

    if st.button("🧠 Solve with A*"):
        path = a_star(board, size)
        if path:
            st.session_state.auto_solve_path = path
            st.success("Auto-solving initiated...")

    if st.button("🔄 Reset Puzzle"):
        st.session_state.board = create_board(size)
        st.session_state.start_time = time.time()
        st.session_state.moves = 0
        st.session_state.auto_solve_path = []
        st.rerun()

    if st.session_state.auto_solve_path:
        with st.expander("📌 Path (A* Solution)", expanded=False):
            st.markdown("#### Detailed Moves:")
            for i, (x, y, nx, ny) in enumerate(st.session_state.auto_solve_path):
                st.markdown(f"<div class='move-info'>Move {i+1}: Tile from ({x}, {y}) → ({nx}, {ny})</div>", unsafe_allow_html=True)

            path_str = " → ".join([f"({x},{y}→{nx},{ny})" for x, y, nx, ny in st.session_state.auto_solve_path])
            st.markdown(f"<div class='compressed-path'>{path_str}</div>", unsafe_allow_html=True)

# --- Win Condition ---
if sum(board, []) == list(range(1, size * size)) + [0]:
    st.balloons()
    st.success(f"🎉 Well done {player_name}! Solved in {st.session_state.moves} moves!")

# --- Auto Solver Animation ---
if st.session_state.auto_solve_path:
    move = st.session_state.auto_solve_path.pop(0)
    x, y, nx, ny = move
    board[x][y], board[nx][ny] = board[nx][ny], board[x][y]
    time.sleep(1.5)
    st.rerun()
