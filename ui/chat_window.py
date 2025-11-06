# ui/chat_window.py
import os, sys, threading, subprocess, time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image

# Optional clipboard copy
try:
    import pyperclip
    HAS_PYPERCLIP = True
except Exception:
    HAS_PYPERCLIP = False

# Allow local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.database import (
    init_db, create_session, list_sessions, get_messages, save_message,
    delete_session, rename_session
)
from modules.retriever import retrieve_chunks
from modules.generator_gemini import generate_answer


# ---------- Helpers ----------
def _reindex():
    """Run FAISS embedding indexer."""
    subprocess.run([sys.executable, "scripts/index_all.py"], check=True)


# ---------- ChatUI ----------
class ChatUI:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.app = ctk.CTk()
        self.app.title("CU AI Assistant")
        self.app.geometry("1100x720")
        self.app.configure(fg_color="#0e0e10")
        init_db()

        # ---------- HEADER ----------
        self.header = ctk.CTkFrame(self.app, fg_color="#1a1a1c", height=75, corner_radius=0)
        self.header.pack(fill="x", side="top")

        logo_path = os.path.join(os.getcwd(), "assets", "cu_logo.png")
        if os.path.exists(logo_path):
            img = Image.open(logo_path).resize((120, 55))
            self.logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 55))
            ctk.CTkLabel(self.header, image=self.logo_img, text="").pack(side="left", padx=(15, 10), pady=8)
        else:
            ctk.CTkLabel(self.header, text="[CU Logo Missing]", text_color="red").pack(side="left", padx=(15, 10))

        title_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        title_frame.pack(side="left", anchor="w", pady=(8, 0))
        ctk.CTkLabel(
            title_frame,
            text="CU AI ASSISTANT",
            text_color="#e50914",
            font=ctk.CTkFont(family="Arial Black", size=26, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_frame,
            text="Your Personal Academic AI",
            text_color="#a8a8a8",
            font=ctk.CTkFont(size=14, slant="italic"),
        ).pack(anchor="w", pady=(2, 0))

        # ---------- MAIN LAYOUT ----------
        self.container = ctk.CTkFrame(self.app, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # ---------- SIDEBAR ----------
        self.sidebar = ctk.CTkFrame(self.container, fg_color="#18181b", corner_radius=15)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=15, pady=15)
        self.sidebar.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self.sidebar,
            text="Chat Sessions",
            text_color="#ffffff",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="center",
        ).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="ew")

        self.session_list = ctk.CTkScrollableFrame(self.sidebar, corner_radius=10, fg_color="#101013")
        self.session_list.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # Sidebar Buttons
        btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.new_btn = ctk.CTkButton(
            btn_frame, text="🆕 New Chat", fg_color="#a259ff", hover_color="#8b45db",
            corner_radius=20, command=self.new_chat
        )
        self.new_btn.pack(fill="x", pady=(0, 8))

        self.reindex_btn = ctk.CTkButton(
            btn_frame, text="🔄 Re-Index PDFs", fg_color="#e50914", hover_color="#b40710",
            corner_radius=20, command=self.reindex_data
        )
        self.reindex_btn.pack(fill="x")

        # ---------- CHAT AREA ----------
        self.chat_frame = ctk.CTkFrame(self.container, fg_color="#111113", corner_radius=15)
        self.chat_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)

        self.msgs = ctk.CTkScrollableFrame(self.chat_frame, corner_radius=15, fg_color="#111113")
        self.msgs.pack(fill="both", expand=True, padx=15, pady=15)
        self.msgs.grid_columnconfigure(0, weight=1)

        # Input Bar
        self.input_frame = ctk.CTkFrame(self.chat_frame, fg_color="#1c1c1f", corner_radius=15)
        self.input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Ask anything related to your academics...",
            fg_color="#0e0e10", border_color="#a259ff", corner_radius=20,
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(10, 10), pady=10, ipady=6)

        self.ask_btn = ctk.CTkButton(
            self.input_frame, text="Ask", fg_color="#a259ff", hover_color="#8b45db",
            corner_radius=20, command=self.on_send,
        )
        self.ask_btn.pack(side="right", padx=(0, 10), pady=10)
        self.entry.bind("<Return>", lambda e: self.on_send())

        # ---------- STATE ----------
        self.current_session_id = None
        self._refresh_sessions()
        if len(self._all_sessions) == 0:
            self.new_chat()
        else:
            sid = self._all_sessions[0][0]
            self.load_session(sid)

    # ---------- SESSION LIST ----------
    def _refresh_sessions(self):
        for w in self.session_list.winfo_children():
            w.destroy()
        self._all_sessions = list_sessions()

        for sid, title in self._all_sessions:
            row = ctk.CTkFrame(self.session_list, fg_color="transparent")
            row.pack(fill="x", pady=3, padx=8)

            name_label = ctk.CTkLabel(row, text=title, anchor="w", text_color="#e0e0e0", font=ctk.CTkFont(size=13))
            name_label.pack(side="left", fill="x", expand=True, padx=(6, 6))
            name_label.bind("<Button-1>", lambda e, s=sid: self.load_session(s))

            # Buttons beside chat
            rename_btn = ctk.CTkButton(
                row, text="✏️", width=30, height=30,
                fg_color="#2563eb", hover_color="#1d4ed8", text_color="white",
                corner_radius=15, command=lambda s=sid: self._rename_chat_inline(s)
            )
            rename_btn.pack(side="right", padx=(4, 4))

            delete_btn = ctk.CTkButton(
                row, text="🗑️", width=30, height=30,
                fg_color="#dc2626", hover_color="#b91c1c", text_color="white",
                corner_radius=15, command=lambda s=sid: self._delete_chat_inline(s)
            )
            delete_btn.pack(side="right", padx=(4, 4))

    def _rename_chat_inline(self, sid):
        new_title = tk.simpledialog.askstring("Rename Chat", "Enter new name:")
        if new_title and new_title.strip():
            rename_session(sid, new_title.strip())
            self._refresh_sessions()

    def _delete_chat_inline(self, sid):
        if messagebox.askyesno("Delete Chat", "Are you sure you want to delete this chat?"):
            delete_session(sid)
            self._refresh_sessions()
            if self.current_session_id == sid:
                for w in self.msgs.winfo_children():
                    w.destroy()
                self.current_session_id = None

    # ---------- CHAT ----------
    def new_chat(self):
        title = f"Chat {len(list_sessions()) + 1}"
        self.current_session_id = create_session(title)
        self._refresh_sessions()
        for w in self.msgs.winfo_children():
            w.destroy()
        self._add_system("🧠 New chat created. Ask your question below.")

    def load_session(self, sid):
        self.current_session_id = sid
        for w in self.msgs.winfo_children():
            w.destroy()
        for role, content in get_messages(sid):
            (self._add_user if role == "user" else self._add_assistant)(content)
        self.msgs._parent_canvas.yview_moveto(1.0)

    def _add_user(self, text):
        row = ctk.CTkFrame(self.msgs, fg_color="transparent")
        row.pack(fill="x", pady=6, padx=10)
        bubble = ctk.CTkFrame(row, fg_color="#2a2d36", corner_radius=20)
        bubble.pack(anchor="e", padx=(120, 0))
        ctk.CTkLabel(bubble, text=text, wraplength=680, justify="left", text_color="#ffffff").pack(padx=12, pady=(10, 6))
        ts = datetime.now().strftime("%I:%M %p").lstrip("0")
        ctk.CTkLabel(bubble, text=ts, text_color="#777777", font=ctk.CTkFont(size=10)).pack(anchor="e", padx=12, pady=(0, 8))

    def _add_assistant(self, text):
        row = ctk.CTkFrame(self.msgs, fg_color="transparent")
        row.pack(fill="x", pady=6, padx=10)
        bubble = ctk.CTkFrame(row, fg_color="#1c1e26", corner_radius=20)
        bubble.pack(anchor="w", padx=(0, 120))
        ctk.CTkLabel(bubble, text=text, wraplength=680, justify="left", text_color="#dcdcdc").pack(padx=12, pady=(10, 6))
        ts = datetime.now().strftime("%I:%M %p").lstrip("0")
        ctk.CTkLabel(bubble, text=ts, text_color="#888888", font=ctk.CTkFont(size=10)).pack(anchor="e", padx=12, pady=(0, 8))
        return bubble

    def _add_system(self, text):
        row = ctk.CTkFrame(self.msgs, fg_color="transparent")
        row.pack(fill="x", pady=8)
        ctk.CTkLabel(row, text=text, text_color="#a259ff", justify="center").pack()
        return row

    # ---------- REINDEX ----------
    def reindex_data(self):
        row = self._add_system("🔄 Re-indexing PDFs and images…")
        progress = ctk.CTkProgressBar(row, width=500, height=12, corner_radius=6,
                                      fg_color="#2a2a2a", progress_color="#e50914")
        progress.pack(pady=(6, 0))
        progress.set(0)
        stop_flag = threading.Event()

        def animate_bar():
            pct = 0
            while not stop_flag.is_set() and pct < 1.0:
                pct += 0.02
                progress.set(pct)
                time.sleep(0.1)
        threading.Thread(target=animate_bar, daemon=True).start()

        def reindex_task():
            try:
                _reindex()
                stop_flag.set()
                progress.set(1.0)
                for w in row.winfo_children():
                    w.destroy()
                ctk.CTkLabel(row, text="✅ Index updated successfully!", text_color="#00ff8c").pack()
            except Exception as e:
                stop_flag.set()
                for w in row.winfo_children():
                    w.destroy()
                ctk.CTkLabel(row, text=f"❌ Indexing failed: {e}", text_color="#ff5577").pack()
        threading.Thread(target=reindex_task, daemon=True).start()

    # ---------- THINKING ----------
    def _show_thinking(self):
        bubble = self._add_assistant("Thinking…")
        label = bubble.winfo_children()[0]
        stop_flag = threading.Event()
        def animate():
            dots = ["Thinking", "Thinking.", "Thinking..", "Thinking..."]
            i = 0
            while not stop_flag.is_set():
                label.configure(text=dots[i % 4])
                i += 1
                time.sleep(0.4)
        threading.Thread(target=animate, daemon=True).start()
        return bubble, stop_flag

    def on_send(self):
        q = self.entry.get().strip()
        if not q:
            return
        if self.current_session_id is None:
            self.new_chat()
        self.entry.delete(0, "end")
        self._add_user(q)
        save_message(self.current_session_id, "user", q)
        self.ask_btn.configure(state="disabled")
        self.thinking_bubble, self.stop_anim = self._show_thinking()
        threading.Thread(target=self._answer_thread, args=(q,), daemon=True).start()

    def _answer_thread(self, q):
        try:
            chunks = retrieve_chunks(q, top_k=8)
            ans = generate_answer(chunks, q) or "I couldn't find a confident answer in the provided material."
            self.stop_anim.set()
            self.thinking_bubble.destroy()
            self._add_assistant(ans)
            save_message(self.current_session_id, "assistant", ans)
        except Exception as e:
            self.stop_anim.set()
            self.thinking_bubble.destroy()
            self._add_system(f"❌ Error: {e}")
        finally:
            self.ask_btn.configure(state="normal")
            self.msgs._parent_canvas.yview_moveto(1.0)


# ---------- Launcher ----------
def launch_ui():
    ChatUI().app.mainloop()
