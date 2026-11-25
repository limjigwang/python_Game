import tkinter as tk
from tkinter import messagebox
import random

ROWS = 10
COLS = 10
MINES = 10

board = []
buttons = []
game_over = False
first_click = True
opened_count = 0
flag_count = 0
elapsed_time = 0
timer_running = False
timer_job = None


def create_board():
    global board
    board = [
        [{"mine": False, "opened": False, "flag": False, "number": 0}
         for _ in range(COLS)]
        for _ in range(ROWS)
    ]

    for position in random.sample(range(ROWS * COLS), MINES):
        r, c = divmod(position, COLS)
        board[r][c]["mine"] = True

    calculate_numbers()


def calculate_numbers():
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c]["mine"]:
                board[r][c]["number"] = 0
                continue

            board[r][c]["number"] = sum(
                1
                for dr in (-1, 0, 1)
                for dc in (-1, 0, 1)
                if (dr != 0 or dc != 0)
                and 0 <= r + dr < ROWS
                and 0 <= c + dc < COLS
                and board[r + dr][c + dc]["mine"]
            )


def update_timer():
    global elapsed_time, timer_job
    if timer_running and not game_over:
        elapsed_time += 1
        time_label.config(text=f"시간: {elapsed_time:03d}")
        timer_job = root.after(1000, update_timer)


def start_timer():
    global timer_running
    if not timer_running:
        timer_running = True
        update_timer()


def open_empty(r, c):
    global opened_count

    if not (0 <= r < ROWS and 0 <= c < COLS):
        return

    cell = board[r][c]
    if cell["opened"] or cell["flag"] or cell["mine"]:
        return

    cell["opened"] = True
    opened_count += 1

    number = cell["number"]
    colors = {
        1: "blue", 2: "green", 3: "red", 4: "purple",
        5: "brown", 6: "darkcyan", 7: "black", 8: "gray"
    }

    buttons[r][c].config(
        text=str(number) if number else "",
        relief="sunken",
        bg="#dddddd",
        fg=colors.get(number, "black"),
        state="disabled"
    )

    if number == 0:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr or dc:
                    open_empty(r + dr, c + dc)


def click_cell(r, c):
    global game_over, first_click, timer_running

    if game_over:
        return

    cell = board[r][c]
    if cell["opened"] or cell["flag"]:
        return

    if first_click:
        first_click = False
        # 첫 클릭이 지뢰라면 다른 위치로 옮겨 안전하게 시작
        if cell["mine"]:
            cell["mine"] = False
            candidates = [
                (i, j) for i in range(ROWS) for j in range(COLS)
                if not board[i][j]["mine"] and (i, j) != (r, c)
            ]
            nr, nc = random.choice(candidates)
            board[nr][nc]["mine"] = True
            calculate_numbers()
        start_timer()

    if cell["mine"]:
        game_over = True
        timer_running = False
        buttons[r][c].config(text="💣", bg="#ff7777", relief="sunken")
        show_all_mines()
        messagebox.showerror("게임 종료", "지뢰를 밟았습니다!")
        return

    open_empty(r, c)
    check_win()


def flag_cell(event, r, c):
    global flag_count

    if game_over:
        return "break"

    cell = board[r][c]
    if cell["opened"]:
        return "break"

    if cell["flag"]:
        cell["flag"] = False
        flag_count -= 1
        buttons[r][c].config(text="")
    else:
        if flag_count >= MINES:
            return "break"
        cell["flag"] = True
        flag_count += 1
        buttons[r][c].config(text="🚩", fg="red")

    mine_label.config(text=f"남은 지뢰: {MINES - flag_count}")
    return "break"


def show_all_mines():
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c]["mine"]:
                buttons[r][c].config(
                    text="💣", bg="#ff9999", relief="sunken"
                )


def check_win():
    global game_over, timer_running
    if opened_count == ROWS * COLS - MINES:
        game_over = True
        timer_running = False
        show_all_mines()
        messagebox.showinfo(
            "게임 승리",
            f"축하합니다! 모든 안전한 칸을 열었습니다.\n기록: {elapsed_time}초"
        )


def new_game():
    global game_over, first_click, opened_count
    global flag_count, elapsed_time, timer_running, timer_job

    if timer_job is not None:
        root.after_cancel(timer_job)
        timer_job = None

    game_over = False
    first_click = True
    opened_count = 0
    flag_count = 0
    elapsed_time = 0
    timer_running = False

    mine_label.config(text=f"남은 지뢰: {MINES}")
    time_label.config(text="시간: 000")

    create_board()

    for widget in game_frame.winfo_children():
        widget.destroy()

    buttons.clear()
    for r in range(ROWS):
        row_buttons = []
        for c in range(COLS):
            btn = tk.Button(
                game_frame,
                text="",
                width=3,
                height=1,
                font=("맑은 고딕", 11, "bold"),
                relief="raised",
                bg="#c9c9c9",
                activebackground="#e0e0e0",
                command=lambda r=r, c=c: click_cell(r, c)
            )
            btn.grid(row=r, column=c, padx=1, pady=1)
            btn.bind(
                "<Button-3>",
                lambda event, r=r, c=c: flag_cell(event, r, c)
            )
            row_buttons.append(btn)
        buttons.append(row_buttons)


root = tk.Tk()
root.title("지뢰찾기 게임")
root.resizable(False, False)
root.configure(bg="#eeeeee")

header = tk.Frame(root, bg="#eeeeee")
header.pack(fill="x", padx=12, pady=12)

mine_label = tk.Label(
    header, text=f"남은 지뢰: {MINES}",
    font=("맑은 고딕", 12, "bold"), bg="#eeeeee"
)
mine_label.pack(side="left", padx=8)

time_label = tk.Label(
    header, text="시간: 000",
    font=("맑은 고딕", 12, "bold"), bg="#eeeeee"
)
time_label.pack(side="left", padx=18)

new_button = tk.Button(
    header, text="새 게임", font=("맑은 고딕", 10),
    command=new_game
)
new_button.pack(side="right", padx=8)

game_frame = tk.Frame(root, bg="#888888", padx=4, pady=4)
game_frame.pack(padx=12, pady=(0, 12))

new_game()
root.mainloop()
