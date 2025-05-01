import streamlit as st
import random
import time
import heapq

# --- Page Config (MUST be first Streamlit command) ---
st.set_page_config(page_title="Colorful Sliding Puzzle", layout="wide")

# --- Music ---
MUSIC_PATH = "https://drive.google.com/uc?export=download&id=1o3H3K6Ns-rGAj5nICxCsRo2_zljma3WP"
st.audio(MUSIC_PATH, format='audio/mp3', start_time=0)

# --- Custom CSS for colorful tiles, sky blue background, and responsiveness ---
st.markdown("""
    <style>
    body {
        background-color: #87CEEB;  /* Sky blue background */
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        font-size: 24px;
        height: 80px;
        border-radius: 12px;
        margin: 4px;
        font-weight: bold;
        transition: all 0.2s ease-in-out;
        background-color: #D8BFD8; /* Ash-Gold Tile Color */
        color: black;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Shadow effect */
    }
    .stButton>button:hover {
        transform: scale(1.1);  /* Enlarge tile on hover */
        background-color: #f1c27d !important;  /* Lighter Ash-Gold on hover */
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2); /* Enlarge shadow on hover */
    }
    .stButton>button:active {
        transform: scale(0.9);  /* Shrink tile when clicked */
        background-color: #f1c27d !important;
    }
    .stTextInput>div>input {
        font-size: 20px;
    }
    .block-container {
        padding-top: 2rem;
    }
    /* Responsive design for smaller screens */
    @media (max-width: 768px) {
        .stButton>button {
            font-size: 18px;
            height: 60px;
        }
        .stTextInput>div>input {
            font-size: 16px;
        }
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
    goal = tuple(tuple((i * size + j + 1) % (size * size) for j in range(size)) for i in range(size))

    open_list = []
    heapq.heappush(open_list, (manhattan_distance(board, size), 0, start, []))
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
                heapq.heappush(open_list, (
                    g + 1 + manhattan_distance(new_board, size),
                    g + 1,
                    new_tuple,
                    path + [(x, y, nx, ny)]
                ))
    return []

# --- Sidebar Login ---
with st.sidebar:
    st.title("Login 🎮")
    player_name = st.text_input("Enter your name:", key="login")
    size = 3  # Fixed to 3x3 only

if not player_name:
    st.warning("Please enter your name to start!")
    st.stop()

# --- Session State ---
if "board" not in st.session_state:
    st.session_state.board = create_board(size)
    st.session_state.start_time = time.time()
    st.session_state.moves = 0
    st.session_state.auto_solve_path = []

board = st.session_state.board

# --- Game Title ---
st.title(f"🎯 Welcome {player_name}! Solve the 3x3 Puzzle")

col1, col2 = st.columns([2, 1])

# --- Puzzle UI ---
with col1:
    for i in range(size):
        cols = st.columns(size)
        for j in range(size):
            tile = board[i][j]
            if tile != 0:
                if cols[j].button(str(tile), use_container_width=True, key=(i,j)):
                    x, y = get_blank(board)
                    if (i, j) in valid_moves(x, y, size):
                        board[x][y], board[i][j] = board[i][j], board[x][y]
                        st.session_state.moves += 1
                        st.rerun()
            else:
                cols[j].empty()

# --- Game Info Panel ---
with col2:
    st.subheader("🧠 Game Info")
    elapsed_time = int(time.time() - st.session_state.start_time)
    st.write(f"⏱️ Time Elapsed: {elapsed_time} sec")
    st.write(f"🕹️ Moves: {st.session_state.moves}")
    st.write(f"📏 Puzzle Size: {size}x{size}")

    if st.button("🧠 Solve with A*"):
        path = a_star(board, size)
        if path:
            st.session_state.auto_solve_path = path
            st.success("Solver is running...")

    if st.button("🔄 Reset Game"):
        st.session_state.board = create_board(size)
        st.session_state.moves = 0
        st.session_state.start_time = time.time()
        st.session_state.auto_solve_path = []
        st.rerun()

    if st.session_state.auto_solve_path:
        st.subheader("📋 A* Move Path:")
        moves_str = "\n".join(
            [f"{i+1}. Move tile {board[x][y]} from ({x},{y}) to ({nx},{ny})"
             for i, (x, y, nx, ny) in enumerate(st.session_state.auto_solve_path)]
        )
        with st.expander("🔍 Show Moves"):
            st.text(moves_str)

# --- Puzzle Completion ---
if sum(board, []) == list(range(1, size * size)) + [0]:
    elapsed_time = int(time.time() - st.session_state.start_time)
    st.balloons()
    st.success(f"🎉 Congrats {player_name}! Solved in {st.session_state.moves} moves and {elapsed_time} seconds!")

# --- Auto-solver animation ---
if st.session_state.auto_solve_path:
    move = st.session_state.auto_solve_path.pop(0)
    x, y, nx, ny = move
    board[x][y], board[nx][ny] = board[nx][ny], board[x][y]
    time.sleep(1)
    st.rerun()
