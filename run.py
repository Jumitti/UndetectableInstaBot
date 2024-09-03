import os
import random
import time
import tkinter as tk
from threading import Thread, Event
import sys
import io
import undetectableinstabot
import platform
import subprocess

# Global variables for comment and emoji lists
comments = []
emojis = []

# Setting the bot
running_event = Event()
reset_event = Event()
like_threshold = 0.75
comment_threshold = 0.49
debug_like = 0
debug_comment = 0


class RedirectText(io.StringIO):
    def __init__(self, text_widget, tag):
        super().__init__()
        self.text_widget = text_widget
        self.tag = tag

    def write(self, text):
        if text:
            self.text_widget.insert(tk.END, text, (self.tag,))
            self.text_widget.see(tk.END)

    def write_log_message(self, text, color="black"):
        self.text_widget.insert(tk.END, text, (color,))
        self.text_widget.see(tk.END)


def load_list_from_file(file_path):
    """Load a list from a text file where each line is an item."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]


def update_comment_list(event=None):
    """Update the comments list based on the selected file."""
    selected_file = comment_list_var.get()
    if selected_file:
        file_path = os.path.join('comment_list', selected_file)
        global comments
        comments = load_list_from_file(file_path)
        log_message(f"Loaded comments from {selected_file}", "purple")


def update_emoji_list(event=None):
    """Update the emoji list based on the selected file."""
    selected_file = emoji_list_var.get()
    if selected_file:
        file_path = os.path.join('comment_list', selected_file)
        global emojis
        emojis = load_list_from_file(file_path)
        log_message(f"Loaded emojis from {selected_file}", "purple")


def generate_simple_comment():
    """Randomly choose a comment and 1 to 3 emojis"""
    comment = random.choice(comments) if comments else ""
    num_emojis = random.randint(1, 3)  # Randomly choose to add 1 or 2 emojis
    emojis_chosen = ''.join(random.choices(emojis, k=num_emojis)) if emojis else ""
    return f"{comment} {emojis_chosen}"


def update_progress(duration=5, text=""):
    """Start loading bar"""
    num_steps = 50
    step_duration = duration / num_steps

    for i in range(num_steps + 1):
        progress = int((i / num_steps) * 100)
        bar = f"[{'#' * i}{'.' * (num_steps - i)}] {progress}%\n{text}"

        progress_text.delete(1.0, tk.END)
        progress_text.insert(tk.END, bar)
        progress_text.update_idletasks()

        time.sleep(step_duration)


def update_progress_bar(fraction, text=""):
    """Progress bar when setting likes and comments"""
    num_steps = 50
    step = int(fraction * num_steps)
    progress = int(fraction * 100)
    bar = f"[{'#' * step}{'.' * (num_steps - step)}] {progress}%\n{text}"

    progress_text.delete(1.0, tk.END)
    progress_text.insert(tk.END, bar)
    progress_text.update_idletasks()


def run_bot():
    global like_threshold, comment_threshold, debug_like, debug_comment
    
    try:
        like_threshold = float(like_threshold_entry.get())
        comment_threshold = float(comment_threshold_entry.get())
        if not (0 <= like_threshold <= 1 and 0 <= comment_threshold <= 1):
            raise ValueError("Thresholds must be between 0 and 1.")
        running_event.set()
    except Exception as e:
        log_message("Thresholds must be between 0 and 1.", "red")
        update_button_state("stopped")

    try:
        if running_event.is_set():
            log_message("Bot started.", "green")
            log_message("Please, move your mouse over the Instagram page", "red")
            update_progress(duration=5, text="Please, move your mouse over the Instagram page")
            update_comment_list()
            update_emoji_list()
            
        while running_event.is_set():
            log_message("Running...", "green")

            sys.stdout = RedirectText(log_text, "green")
            sys.stderr = RedirectText(log_text, "red")

            # Like
            if like_threshold < 1:
                scale_like, maxval_like = undetectableinstabot.main_like(debug=debug_like, threshold=like_threshold, update_progress_callback=update_progress_bar)
                if not running_event.is_set() or reset_event.is_set():
                    break

                if scale_like and maxval_like:
                    like_result_label.config(text=f"Like Thr. found\nMax Thr.: {maxval_like:.2f}\nScale: {scale_like:.2f}", fg='green')
                else:
                    like_result_label.config(text=f"Like Thr. found\nMax Thr.: Not found\nScale: Not found", fg='red')

            # Comment
            if comment_threshold < 1:
                scale_com, maxval_com = undetectableinstabot.main_comment(generate_simple_comment(), debug=debug_comment, threshold=comment_threshold, update_progress_callback=update_progress_bar)
                if not running_event.is_set() or reset_event.is_set():
                    break
                    
                if scale_com and maxval_com:
                    comment_result_label.config(text=f"Com. Thr. found\nMax Thr.: {maxval_com:.2f}\nScale: {scale_com:.2f}", fg='green')
                else:
                    comment_result_label.config(text=f"Com. Thr. found\nMax Thr.: Not found\nScale: Not found", fg='red')

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            time.sleep(0.5)

    finally:
        if reset_event.is_set():
            undetectableinstabot.reset()
        log_message("Bot stopped or paused.", "gray")


def start_bot():
    if running_event.is_set():
        log_message("Bot is already running.", "red")
        return
    running_event.clear()
    reset_event.clear()
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
    update_button_state("started")


def pause_bot():
    running_event.clear()
    log_message("Pausing bot...", "orange")
    undetectableinstabot.reset(pause=True)
    update_button_state("paused")


def stop_bot():
    log_message("Stopping bot...", "blue")
    if not running_event.is_set():
        log_message("Bot stopped", "gray")
    running_event.clear()
    reset_event.set()
    undetectableinstabot.reset()
    update_button_state("stopped")


def update_debug_like():
    global debug_like
    if debug_like_var2.get():
        debug_like = 2
    elif debug_like_var1.get():
        debug_like = 1
    else:
        debug_like = 0
    update_bot_settings()


def update_debug_comment():
    global debug_comment
    if debug_comment_var2.get():
        debug_comment = 2
    elif debug_comment_var1.get():
        debug_comment = 1
    else:
        debug_comment = 0
    update_bot_settings()


def update_bot_settings():
    if running_event.is_set():
        stop_bot()
        time.sleep(1)
        start_bot()


def update_button_state(state):
    if state == "started":
        start_button.config(state=tk.DISABLED)
        pause_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.NORMAL)
    elif state == "stopped":
        start_button.config(state=tk.NORMAL)
        pause_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.DISABLED)
    elif state == "paused":
        start_button.config(state=tk.NORMAL)
        pause_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)


def toggle_debug_like():
    if debug_like_var2.get():
        debug_like_var1.set(False)
    update_debug_like()


def toggle_debug_like2():
    if debug_like_var1.get():
        debug_like_var2.set(False)
    update_debug_like()


def toggle_debug_comment():
    if debug_comment_var2.get():
        debug_comment_var1.set(False)
    update_debug_comment()


def toggle_debug_comment2():
    if debug_comment_var1.get():
        debug_comment_var2.set(False)
    update_debug_comment()


def open_debug_folder():
    if platform.system() == "Windows":
        os.startfile("debug")
    elif platform.system() == "Darwin":  # macOS
        subprocess.Popen(["open", "debug"])
    else:  # Linux
        subprocess.Popen(["xdg-open", "debug"])


def log_message(message, color="black"):
    sys.stdout = RedirectText(log_text, color)
    sys.stderr = RedirectText(log_text, "red")
    sys.stdout.write_log_message(message + "\n", color)


# Tkinter
window = tk.Tk()
window.title("UndetectableInstaBot")

# Left and Right frame
command_frame = tk.Frame(window)
command_frame.pack(side=tk.LEFT, padx=10, pady=10)

logs_frame = tk.Frame(window)
logs_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create a frame for thresholds
thresholds_frame = tk.Frame(command_frame)
thresholds_frame.pack(pady=5)

# Add the like threshold label and entry
like_threshold_label = tk.Label(thresholds_frame, text="Like Threshold (0-1)\n(Default: 0.75 | 1 to disable)")
like_threshold_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
like_threshold_entry = tk.Entry(thresholds_frame)
like_threshold_entry.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
like_threshold_entry.insert(0, str(like_threshold))

# Add the comment threshold label and entry
comment_threshold_label = tk.Label(thresholds_frame, text="Comment Threshold\n(Default: 0.49 | 1 to disable)")
comment_threshold_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
comment_threshold_entry = tk.Entry(thresholds_frame)
comment_threshold_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
comment_threshold_entry.insert(0, str(comment_threshold))

# Frame for settings under thresholds
results_frame = tk.Frame(command_frame)
results_frame.pack(pady=5)

like_result_label = tk.Label(results_frame, text="", fg='black')
like_result_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

comment_result_label = tk.Label(results_frame, text="", fg='black')
comment_result_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

# Comment an emoji lists
comment_list_var = tk.StringVar()
emoji_list_var = tk.StringVar()

comment_files = [f for f in os.listdir('comment_list') if f.endswith('.txt')]
emoji_files = comment_files

dropdown_frame = tk.Frame(command_frame)
dropdown_frame.pack(pady=5)

comment_label = tk.Label(dropdown_frame, text="Comment")
comment_label.grid(row=0, column=0, padx=5)
comment_list_menu = tk.OptionMenu(dropdown_frame, comment_list_var, *comment_files, command=update_comment_list)
comment_list_menu.grid(row=1, column=0, padx=5)
comment_list_var.set(comment_files[0])

emoji_label = tk.Label(dropdown_frame, text="Emoji\n(Use empty.txt for use one list)")
emoji_label.grid(row=0, column=1, padx=5)
emoji_list_menu = tk.OptionMenu(dropdown_frame, emoji_list_var, *emoji_files, command=update_emoji_list)
emoji_list_menu.grid(row=1, column=1, padx=5)
emoji_list_var.set(emoji_files[0])

# Start Pause Stop buttons
button_frame = tk.Frame(command_frame)
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="Start Bot", command=start_bot)
start_button.grid(row=0, column=0, padx=5)

pause_button = tk.Button(button_frame, text="Pause Bot", command=pause_bot, state=tk.DISABLED)
pause_button.grid(row=0, column=1, padx=5)

stop_button = tk.Button(button_frame, text="Stop Bot", command=stop_bot, state=tk.DISABLED)
stop_button.grid(row=0, column=2, padx=5)

# Debug options for like
debug_like_var1 = tk.BooleanVar()
debug_like_var2 = tk.BooleanVar()

debug_like_frame = tk.LabelFrame(command_frame, text="Like Debug Options", padx=10, pady=10)
debug_like_frame.pack(padx=10, pady=10, fill="x")

debug_like_detected = tk.Checkbutton(debug_like_frame, text="Detected", variable=debug_like_var1, command=toggle_debug_like)
debug_like_detected.grid(row=0, column=0, padx=5)

debug_like_detection_detected = tk.Checkbutton(debug_like_frame, text="Detection + Detected", variable=debug_like_var2, command=toggle_debug_like2)
debug_like_detection_detected.grid(row=0, column=1, padx=5)

# Debug options for comment
debug_comment_var1 = tk.BooleanVar()
debug_comment_var2 = tk.BooleanVar()

debug_comment_frame = tk.LabelFrame(command_frame, text="Comment Debug Options", padx=10, pady=10)
debug_comment_frame.pack(padx=10, pady=10, fill="x")

debug_comment_detected = tk.Checkbutton(debug_comment_frame, text="Detected", variable=debug_comment_var1, command=toggle_debug_comment)
debug_comment_detected.grid(row=0, column=0, padx=5)

debug_comment_detection_detected = tk.Checkbutton(debug_comment_frame, text="Detection + Detected", variable=debug_comment_var2, command=toggle_debug_comment2)
debug_comment_detection_detected.grid(row=0, column=1, padx=5)

# Add the "Open debug folder" button
open_debug_button = tk.Button(command_frame, text="Open debug folder", command=open_debug_folder)
open_debug_button.pack(pady=10)

# Logs
log_frame = tk.Frame(logs_frame)
log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Progress bar
progress_frame = tk.Frame(logs_frame)
progress_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(10, 0))

# Displaying logs
log_text = tk.Text(log_frame, wrap=tk.WORD, height=21, width=60)
log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(log_frame, command=log_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_text.config(yscrollcommand=scrollbar.set)
log_text.tag_configure("red", foreground="red")
log_text.tag_configure("green", foreground="green")
log_text.tag_configure("blue", foreground="blue")
log_text.tag_configure("purple", foreground="purple")
log_text.tag_configure("orange", foreground="orange")
log_text.tag_configure("gray", foreground="gray")

# Progress bar
progress_text = tk.Text(progress_frame, wrap=tk.WORD, height=3, width=60)
progress_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Redirect stdout and stderr
redirect_stdout = RedirectText(log_text, "black")
redirect_stderr = RedirectText(log_text, "red")
sys.stdout = redirect_stdout
sys.stderr = redirect_stderr

# Initial button state setup
update_button_state("stopped")

# Start TKinter
window.mainloop()
