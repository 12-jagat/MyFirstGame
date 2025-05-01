import streamlit as st
import random
import copy
import time
import heapq

# ✅ MUST be first Streamlit command
st.set_page_config(page_title="Colorful Sliding Puzzle", layout="wide")

# --- Custom CSS for styling ---
st.markdown("""
    <style>
        .title {
            text-align: center;
            color: #2c3e50;
            font-size: 36px;
            font-weight: bold;
        }
        .stButton > button {
            background-color: #3498db;
            color: white;
            border-radius: 10px;
            font-size: 24px;
            height: 80px;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #2980b9;
        }
        .sidebar .sidebar-content {
            background-color: #ecf0f1;
        }
        .highlight-box {
            background-color: #dff9fb;
            padding: 10px;
            border-radius: 8px;
            font-size: 18px;
        }
        .dropdown-style {
            background-color: #fefefe;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 10px;
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

# --- A* Algorithm ---
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
    goal = tuple(tuple((i * size + j + 1) % (size * size) for j in range(size)) for i in range(size))

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

# --- Sidebar Login ---
with st.sidebar:
    st.title("Login")
    player_name = st.text_input("Enter your name:", key="login")
    size = st.selectbox("Select Puzzle Size:", (3,))  # Only 3x3 supported for now

if not player_name:
    st.warning("Please enter your name to start!")
    st.stop()

# --- Session State Init ---
if "board" not in st.session_state:
    st.session_state.board = create_board(size)
    st.session_state.start_time = time.time()
    st.session_state.moves = 0
    st.session_state.auto_solve_path = []

board = st.session_state.board

# --- Title ---
st.markdown(f"<div class='title'>🎯 Welcome {player_name}! Solve the 3x3 Sliding Puzzle</div>", unsafe_allow_html=True)

# --- Puzzle Area & Info ---
col1, col2 = st.columns([2, 1])

with col1:
    for i in range(size):
        cols = st.columns(size)
        for j in range(size):
            if board[i][j] != 0:
                if cols[j].button(str(board[i][j]), use_container_width=True, key=(i, j)):
                    x, y = get_blank(board)
                    if (i, j) in valid_moves(x, y, size):
                        board[x][y], board[i][j] = board[i][j], board[x][y]
                        st.session_state.moves += 1
                        st.rerun()

with col2:
    st.subheader("Game Info")
    elapsed_time = int(time.time() - st.session_state.start_time)
    st.markdown(f"<div class='highlight-box'>⏱️ Time Elapsed: {elapsed_time} seconds</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='highlight-box'>🎮 Moves Made: {st.session_state.moves}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='highlight-box'>📐 Puzzle Size: {size}x{size}</div>", unsafe_allow_html=True)

    if st.button("Solve with A*"):
        path = a_star(board, size)
        if path:
            st.session_state.auto_solve_path = path
            st.success("✅ Auto-solving started!")

    if st.button("🔄 Reset Game"):
        st.session_state.board = create_board(size)
        st.session_state.moves = 0
        st.session_state.start_time = time.time()
        st.session_state.auto_solve_path = []
        st.rerun()

    # 🔽 Dropdown for path
    with st.expander("📜 View A* Path Steps"):
        if st.session_state.auto_solve_path:
            moves_str = "\n".join([
                f"Move {i+1}: Tile {board[x][y]} from ({x}, {y}) → ({nx}, {ny})"
                for i, (x, y, nx, ny) in enumerate(st.session_state.auto_solve_path)
            ])
            st.text(moves_str)

            final_path_str = " → ".join([f"({x},{y})→({nx},{ny})" for x, y, nx, ny in st.session_state.auto_solve_path])
            st.markdown(f"**Final Path String:** `{final_path_str}`")

# --- Win Condition ---
if sum(board, []) == list(range(1, size*size)) + [0]:
    elapsed_time = int(time.time() - st.session_state.start_time)
    st.balloons()
    st.success(f"🎉 Congratulations {player_name}! You solved it in {st.session_state.moves} moves and {elapsed_time} seconds!")

# --- Animate Auto-Solving ---
if st.session_state.auto_solve_path:
    move = st.session_state.auto_solve_path.pop(0)
    x, y, nx, ny = move
    board[x][y], board[nx][ny] = board[nx][ny], board[x][y]
    time.sleep(0.8)
    st.rerun()
