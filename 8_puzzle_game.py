import streamlit as st
import random
import time
import heapq

# Must be first command
st.set_page_config(page_title="Sliding Puzzle Game", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
        .title {
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            color: #273c75;
        }
        .stButton>button {
            font-size: 24px;
            height: 80px;
            width: 100%;
            border-radius: 12px;
            background-color: #74b9ff;
            color: #fff;
            transition: 0.3s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #0984e3;
            transform: scale(1.05);
        }
        .highlight {
            background-color: #dff9fb;
            padding: 10px;
            border-radius: 8px;
            font-size: 18px;
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
        for j in range(len(board[i])):
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
                tx, ty = divmod(val - 1, size)
                dist += abs(i - tx) + abs(j - ty)
    return dist

def a_star(board, size):
    start = tuple(tuple(row) for row in board)
    goal = tuple(tuple((i * size + j + 1) % (size * size) for j in range(size)) for i in range(size))

    heap = [(manhattan_distance(board, size), 0, start, [])]
    visited = set()
    visited.add(start)

    while heap:
        _, g, state, path = heapq.heappop(heap)
        if state == goal:
            return path

        x, y = get_blank(state)
        for nx, ny in valid_moves(x, y, size):
            new_board = [list(row) for row in state]
            new_board[x][y], new_board[nx][ny] = new_board[nx][ny], new_board[x][y]
            new_state = tuple(tuple(row) for row in new_board)
            if new_state not in visited:
                visited.add(new_state)
                heapq.heappush(heap, (
                    g + 1 + manhattan_distance(new_board, size),
                    g + 1,
                    new_state,
                    path + [(x, y, nx, ny)]
                ))
    return []

# --- Sidebar Login ---
with st.sidebar:
    st.title("🧩 Puzzle Options")
    name = st.text_input("Enter your name:")
    size = st.selectbox("Select grid size:", [3, 4])

if not name:
    st.warning("Please enter your name in sidebar.")
    st.stop()

# --- Init Session ---
if "board" not in st.session_state or "size" not in st.session_state or st.session_state.size != size:
    st.session_state.board = create_board(size)
    st.session_state.start_time = time.time()
    st.session_state.moves = 0
    st.session_state.auto_path = []
    st.session_state.size = size

board = st.session_state.board

# --- Title ---
st.markdown(f"<div class='title'>🎯 {name}'s {size}x{size} Sliding Puzzle</div>", unsafe_allow_html=True)

# --- Puzzle Grid ---
cols = st.columns(size)
for i in range(size):
    row = st.columns(size)
    for j in range(size):
        if board[i][j] != 0:
            if row[j].button(str(board[i][j]), key=f"{i}-{j}"):
                x, y = get_blank(board)
                if (i, j) in valid_moves(x, y, size):
                    board[x][y], board[i][j] = board[i][j], board[x][y]
                    st.session_state.moves += 1
                    st.rerun()
        else:
            row[j].markdown("### ▢")

# --- Info + Controls ---
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"<div class='highlight'>⏱️ Time: {int(time.time() - st.session_state.start_time)}s</div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='highlight'>🔁 Moves: {st.session_state.moves}</div>", unsafe_allow_html=True)
with c3:
    if st.button("🔄 Reset"):
        st.session_state.board = create_board(size)
        st.session_state.moves = 0
        st.session_state.start_time = time.time()
        st.session_state.auto_path = []
        st.rerun()

st.markdown("---")
if st.button("🧠 Auto-Solve with A*"):
    path = a_star(board, size)
    if path:
        st.session_state.auto_path = path
        st.success("Auto-solving started...")
        st.rerun()
    else:
        st.error("No path found!")

# --- Animate Path ---
if st.session_state.auto_path:
    move = st.session_state.auto_path.pop(0)
    x, y, nx, ny = move
    board[x][y], board[nx][ny] = board[nx][ny], board[x][y]
    time.sleep(0.5)
    st.rerun()

# --- Win Message ---
flat = sum(board, [])
if flat == list(range(1, size * size)) + [0]:
    st.success(f"🎉 Well done, {name}! Solved in {st.session_state.moves} moves and {int(time.time() - st.session_state.start_time)} seconds!")
    st.balloons()
