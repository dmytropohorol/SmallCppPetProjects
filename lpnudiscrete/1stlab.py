# GUI for building inverse relation matrix p^{-1} from keyboard-like input.
# Uses Tkinter (in the Python standard library).

import tkinter as tk
from tkinter import ttk, messagebox

from typing import List, Tuple


# ---------- Helpers ----------
def dedup_preserve_order(seq: List[str]) -> List[str]:
    """Remove duplicates while preserving order."""
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def parse_pair(line: str) -> Tuple[str, str]:
    """Parse a pair like 'a b', 'a,b', '(a,b)', '[a,b]' into ('a','b')."""
    normalized = (
        line.strip()
            .replace("(", " ")
            .replace(")", " ")
            .replace("[", " ")
            .replace("]", " ")
            .replace(",", " ")
    )
    tokens = [t for t in normalized.split() if t]
    if len(tokens) < 2:
        raise ValueError(f"Cannot parse pair from: {line!r}")
    return tokens[0], tokens[1]

def build_matrix(A: List[str], pairs: List[Tuple[str, str]]) -> List[List[int]]:
    """Build adjacency matrix of relation p over ordered set A."""
    n = len(A)
    idx = {a: i for i, a in enumerate(A)}
    M = [[0] * n for _ in range(n)]
    for x, y in pairs:
        if x in idx and y in idx:
            M[idx[x]][idx[y]] = 1
    return M

def transpose(M: List[List[int]]) -> List[List[int]]:
    return [list(row) for row in zip(*M)] if M else []


# ---------- UI Components ----------
class MatrixTable(ttk.Frame):
    """A labeled matrix table using ttk.Treeview."""
    def __init__(self, parent, title: str, A: List[str], M: List[List[int]]):
        super().__init__(parent)
        self.title_label = ttk.Label(self, text=title, font=("Segoe UI", 10, "bold"))
        self.title_label.pack(anchor="w", pady=(4, 2))

        if not A:
            ttk.Label(self, text="(empty set A)").pack(anchor="w")
            return

        cols = [""] + A  # first blank column for row labels
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=min(12, len(A) + 1))
        # Headings
        self.tree.heading(cols[0], text="A \\ A")
        self.tree.column(cols[0], width=120, stretch=False, anchor="center")
        for a in A:
            self.tree.heading(a, text=str(a))
            self.tree.column(a, width=max(60, 20 + 10 * max(1, len(str(a)))), stretch=False, anchor="center")

        # Rows
        for i, row_label in enumerate(A):
            row_vals = [row_label] + [M[i][j] for j in range(len(A))]
            self.tree.insert("", "end", values=row_vals)

        self.tree.pack(fill="x")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inverse Relation Matrix (p⁻¹)")
        self.geometry("820x600")
        self.minsize(740, 520)

        # Styles
        style = ttk.Style(self)
        style.configure("TLabel", padding=2)
        style.configure("TEntry", padding=2)
        style.configure("TButton", padding=4)

        # ---- Input section ----
        input_frame = ttk.LabelFrame(self, text="Input")
        input_frame.pack(fill="x", padx=10, pady=10)

        # Set A
        a_row = ttk.Frame(input_frame)
        a_row.pack(fill="x", padx=8, pady=6)
        ttk.Label(a_row, text="Set A (space/comma separated) — optional:").pack(side="left")
        self.entry_A = ttk.Entry(a_row)
        self.entry_A.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self.entry_A.insert(0, "")  # leave empty to infer from pairs

        # Hint
        hint = ttk.Label(
            input_frame,
            foreground="#555",
            text="Pairs: one per line. Formats supported: 'a b', 'a,b', '(a,b)'. Example:\na b\nb c\nc a"
        )
        hint.pack(anchor="w", padx=8, pady=(0, 6))

        # Pairs text area
        pairs_frame = ttk.Frame(input_frame)
        pairs_frame.pack(fill="both", padx=8, pady=(0, 6))
        self.text_pairs = tk.Text(pairs_frame, height=7, wrap="none")
        self.text_pairs.pack(side="left", fill="both", expand=True)
        scroll_y = ttk.Scrollbar(pairs_frame, orient="vertical", command=self.text_pairs.yview)
        scroll_y.pack(side="right", fill="y")
        self.text_pairs.configure(yscrollcommand=scroll_y.set)

        # Buttons
        btn_row = ttk.Frame(input_frame)
        btn_row.pack(fill="x", padx=8, pady=6)
        self.btn_compute = ttk.Button(btn_row, text="Compute", command=self.on_compute)
        self.btn_compute.pack(side="left")
        ttk.Button(btn_row, text="Clear", command=self.on_clear).pack(side="left", padx=8)

        # ---- Output section ----
        self.output_frame = ttk.LabelFrame(self, text="Output")
        self.output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # container inside output for dynamic tables
        self.tables_container = ttk.Frame(self.output_frame)
        self.tables_container.pack(fill="both", expand=True, padx=8, pady=8)

        # status
        self.status = ttk.Label(self, anchor="w")
        self.status.pack(fill="x", padx=10, pady=(0, 10))

        # Prefill a tiny example
        self.text_pairs.insert("1.0", "a b\nb c\nc a")

    def on_clear(self):
        self.entry_A.delete(0, "end")
        self.text_pairs.delete("1.0", "end")
        for child in list(self.tables_container.winfo_children()):
            child.destroy()
        self.status.config(text="Cleared.")

    def parse_inputs(self):
        # Parse set A (optional)
        raw_A = self.entry_A.get().strip()
        A = []
        if raw_A:
            # Split by whitespace or commas
            tokens = [t for t in raw_A.replace(",", " ").split() if t]
            A = dedup_preserve_order(tokens)

        # Parse pairs (required)
        raw_pairs = self.text_pairs.get("1.0", "end").strip().splitlines()
        pairs = []
        elems_seen = []
        errors = []
        for ln, line in enumerate(raw_pairs, start=1):
            if not line.strip():
                continue
            try:
                x, y = parse_pair(line)
                pairs.append((x, y))
                elems_seen.extend([x, y])
            except ValueError as e:
                errors.append(f"Line {ln}: {e}")

        if errors:
            messagebox.showwarning("Parse warnings", "\n".join(errors))

        if not pairs:
            raise ValueError("No valid pairs were provided.")

        # If A was not given, infer from pairs
        if not A:
            A = dedup_preserve_order(elems_seen)

        return A, pairs

    def on_compute(self):
        try:
            A, pairs = self.parse_inputs()
        except ValueError as e:
            messagebox.showerror("Input error", str(e))
            return

        # Filter pairs outside A if user explicitly set A
        raw_A = self.entry_A.get().strip()
        if raw_A:
            outside = [(x, y) for (x, y) in pairs if x not in A or y not in A]
            if outside:
                msg = "Some pairs contain elements not in A and were ignored:\n" + \
                      ", ".join(f"({x},{y})" for x, y in outside)
                messagebox.showinfo("Notice", msg)
            pairs = [(x, y) for (x, y) in pairs if x in A and y in A]

        # Build matrices
        M_p = build_matrix(A, pairs)
        M_p_inv = transpose(M_p)

        # Clear previous tables
        for child in list(self.tables_container.winfo_children()):
            child.destroy()

        # Render two tables
        tbl1 = MatrixTable(self.tables_container, "Matrix of relation p", A, M_p)
        tbl1.pack(fill="x", pady=(0, 10))
        tbl2 = MatrixTable(self.tables_container, "Matrix of inverse relation p⁻¹", A, M_p_inv)
        tbl2.pack(fill="x")

        self.status.config(text=f"|A| = {len(A)}; Pairs used = {sum(sum(r) for r in M_p)}; p⁻¹ equals transpose(p).")


if __name__ == "__main__":
    App().mainloop()