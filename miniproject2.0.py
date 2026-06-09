"""
╔══════════════════════════════════════════╗
║       BANK MANAGEMENT SYSTEM             ║
║       GUI Version — Built with Tkinter   ║
╚══════════════════════════════════════════╝
"""

import json
import os
import hashlib
import datetime
import random
import tkinter as tk
from tkinter import ttk, messagebox

# ─────────────────────────────────────────
#  CONSTANTS & COLORS
# ─────────────────────────────────────────
BG        = "#F7F8FA"
WHITE     = "#FFFFFF"
PRIMARY   = "#2563EB"
PRIMARY_H = "#1D4ED8"
SUCCESS   = "#16A34A"
DANGER    = "#DC2626"
TEXT      = "#1E293B"
MUTED     = "#64748B"
BORDER    = "#E2E8F0"
CARD_BG   = "#FFFFFF"
ENTRY_BG  = "#F1F5F9"

DATA_FILE = "bank_data.json"

# ─────────────────────────────────────────
#  DATA HELPERS
# ─────────────────────────────────────────
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def generate_account_number():
    data = load_data()
    while True:
        acc_no = str(random.randint(1000000000, 9999999999))
        if acc_no not in data:
            return acc_no

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ─────────────────────────────────────────
#  REUSABLE WIDGET HELPERS
# ─────────────────────────────────────────
def styled_frame(parent, **kw):
    return tk.Frame(parent, bg=kw.get("bg", BG), **{k: v for k, v in kw.items() if k != "bg"})

def card(parent, padx=24, pady=20):
    f = tk.Frame(parent, bg=CARD_BG, relief="flat",
                 highlightthickness=1, highlightbackground=BORDER)
    f.pack(fill="x", padx=padx, pady=(0, 14))
    tk.Frame(f, bg=CARD_BG, height=pady).pack()
    return f

def label(parent, text, size=13, color=TEXT, bold=False, anchor="w"):
    font = ("Segoe UI", size, "bold" if bold else "normal")
    return tk.Label(parent, text=text, font=font, fg=color,
                    bg=parent.cget("bg"), anchor=anchor)

def entry(parent, show=None, width=36):
    e = tk.Entry(parent, font=("Segoe UI", 12), fg=TEXT, bg=ENTRY_BG,
                 relief="flat", highlightthickness=1,
                 highlightbackground=BORDER, highlightcolor=PRIMARY,
                 width=width, show=show or "")
    e.pack(fill="x", ipady=7, pady=(3, 10))
    return e

def btn(parent, text, command, color=PRIMARY, fg="white", full=True):
    b = tk.Button(parent, text=text, command=command,
                  font=("Segoe UI", 12, "bold"), fg=fg, bg=color,
                  activebackground=PRIMARY_H, activeforeground="white",
                  relief="flat", cursor="hand2", pady=9)
    if full:
        b.pack(fill="x", pady=(4, 0))
    else:
        b.pack(side="left", padx=(0, 8), pady=(4, 0))
    return b

def link_btn(parent, text, command):
    b = tk.Button(parent, text=text, command=command,
                  font=("Segoe UI", 11, "underline"), fg=PRIMARY,
                  bg=parent.cget("bg"), relief="flat",
                  cursor="hand2", bd=0, activeforeground=PRIMARY_H,
                  activebackground=parent.cget("bg"))
    b.pack()
    return b

def divider(parent):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=12)

def section_title(parent, text):
    f = tk.Frame(parent, bg=BG)
    f.pack(fill="x", padx=24, pady=(18, 4))
    label(f, text, size=11, color=MUTED).pack(anchor="w")

# ─────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────
class BankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bank Management System")
        self.geometry("480x640")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.current_acc = None
        self._frame = None
        self.show_home()

    def switch(self, frame_class, *args):
        if self._frame:
            self._frame.destroy()
        self._frame = frame_class(self, *args)
        self._frame.pack(fill="both", expand=True)

    def show_home(self):
        self.switch(HomeScreen)

    def show_create(self):
        self.switch(CreateAccountScreen)

    def show_login(self):
        self.switch(LoginScreen)

    def show_dashboard(self, acc_no):
        self.current_acc = acc_no
        self.switch(DashboardScreen, acc_no)

    def show_deposit(self, acc_no):
        self.switch(DepositScreen, acc_no)

    def show_withdraw(self, acc_no):
        self.switch(WithdrawScreen, acc_no)

    def show_transfer(self, acc_no):
        self.switch(TransferScreen, acc_no)

    def show_balance(self, acc_no):
        self.switch(BalanceScreen, acc_no)

    def show_history(self, acc_no):
        self.switch(HistoryScreen, acc_no)

    def show_delete(self, acc_no):
        self.switch(DeleteScreen, acc_no)

# ─────────────────────────────────────────
#  SCROLLABLE BASE
# ─────────────────────────────────────────
class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.inner = tk.Frame(canvas, bg=BG)
        self.inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

# ─────────────────────────────────────────
#  TOP BAR
# ─────────────────────────────────────────
def topbar(parent, title, back_cmd=None):
    bar = tk.Frame(parent, bg=PRIMARY, height=56)
    bar.pack(fill="x")
    bar.pack_propagate(False)
    if back_cmd:
        tk.Button(bar, text="←", font=("Segoe UI", 16), fg="white",
                  bg=PRIMARY, activebackground=PRIMARY_H,
                  activeforeground="white", relief="flat",
                  cursor="hand2", command=back_cmd).pack(side="left", padx=12)
    tk.Label(bar, text=title, font=("Segoe UI", 14, "bold"),
             fg="white", bg=PRIMARY).pack(side="left", padx=(4 if back_cmd else 16, 0))

# ─────────────────────────────────────────
#  HOME SCREEN
# ─────────────────────────────────────────
class HomeScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        # Hero
        hero = tk.Frame(self, bg=PRIMARY, height=200)
        hero.pack(fill="x")
        hero.pack_propagate(False)
        tk.Label(hero, text="🏦", font=("Segoe UI", 42),
                 bg=PRIMARY).pack(pady=(28, 4))
        tk.Label(hero, text="Bank Management System",
                 font=("Segoe UI", 15, "bold"), fg="white", bg=PRIMARY).pack()
        tk.Label(hero, text="Secure · Simple · Reliable",
                 font=("Segoe UI", 11), fg="#BFDBFE", bg=PRIMARY).pack()

        tk.Frame(self, bg=BG, height=32).pack()

        c = card(self, padx=32, pady=24)
        label(c, "Welcome", size=18, bold=True, anchor="center").pack(pady=(0, 4))
        label(c, "Please choose an option to get started.",
              size=12, color=MUTED, anchor="center").pack(pady=(0, 18))

        btn(c, "  Create New Account", app.show_create if False else self.app.show_create,
            color=PRIMARY)
        tk.Frame(c, bg=CARD_BG, height=8).pack()
        btn(c, "  Login to Account", self.app.show_login,
            color=SUCCESS)
        tk.Frame(c, bg=CARD_BG, height=8).pack()
        btn(c, "  Exit", self.app.destroy,
            color=DANGER)
        tk.Frame(c, bg=CARD_BG, height=8).pack()

# ─────────────────────────────────────────
#  CREATE ACCOUNT SCREEN
# ─────────────────────────────────────────
class CreateAccountScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        topbar(self, "Create Account", self.app.show_home)
        sf = ScrollFrame(self)
        sf.pack(fill="both", expand=True)
        p = sf.inner

        tk.Frame(p, bg=BG, height=16).pack()

        c = card(p, padx=24)

        label(c, "Full Name").pack(anchor="w", padx=16)
        self.name_e = entry(c); self.name_e.pack_configure(padx=16)

        label(c, "Phone Number (10 digits)").pack(anchor="w", padx=16)
        self.phone_e = entry(c); self.phone_e.pack_configure(padx=16)

        label(c, "4-digit PIN").pack(anchor="w", padx=16)
        self.pin_e = entry(c, show="●"); self.pin_e.pack_configure(padx=16)

        label(c, "Confirm PIN").pack(anchor="w", padx=16)
        self.cpin_e = entry(c, show="●"); self.cpin_e.pack_configure(padx=16)

        label(c, "Initial Deposit (₹) — min ₹500").pack(anchor="w", padx=16)
        self.dep_e = entry(c); self.dep_e.pack_configure(padx=16)

        tk.Frame(c, bg=CARD_BG, height=4).pack()
        f = tk.Frame(c, bg=CARD_BG)
        f.pack(fill="x", padx=16, pady=(0, 16))
        btn(f, "Create Account", self._create, full=False)

        tk.Frame(p, bg=BG, height=24).pack()

    def _create(self):
        name  = self.name_e.get().strip()
        phone = self.phone_e.get().strip()
        pin   = self.pin_e.get().strip()
        cpin  = self.cpin_e.get().strip()
        dep   = self.dep_e.get().strip()

        if not name:
            return messagebox.showerror("Error", "Name cannot be empty.")
        if not phone.isdigit() or len(phone) != 10:
            return messagebox.showerror("Error", "Enter a valid 10-digit phone number.")
        if not pin.isdigit() or len(pin) != 4:
            return messagebox.showerror("Error", "PIN must be exactly 4 digits.")
        if pin != cpin:
            return messagebox.showerror("Error", "PINs do not match.")
        try:
            dep_amt = float(dep)
            if dep_amt < 500:
                return messagebox.showerror("Error", "Minimum initial deposit is ₹500.")
        except ValueError:
            return messagebox.showerror("Error", "Invalid deposit amount.")

        acc_no = generate_account_number()
        data = load_data()
        data[acc_no] = {
            "name": name, "phone": phone, "pin": hash_pin(pin),
            "balance": dep_amt, "created_on": get_timestamp(),
            "transactions": [{
                "type": "Account Opened / Initial Deposit",
                "amount": dep_amt, "date": get_timestamp(),
                "balance_after": dep_amt,
            }]
        }
        save_data(data)
        self.app.switch(AccountCreatedScreen, acc_no, name, dep_amt)

# ─────────────────────────────────────────
#  ACCOUNT CREATED CONFIRMATION
# ─────────────────────────────────────────
class AccountCreatedScreen(tk.Frame):
    def __init__(self, app, acc_no, name, balance):
        super().__init__(app, bg=BG)
        self.app = app
        topbar(self, "Account Created")
        tk.Frame(self, bg=BG, height=32).pack()

        c = card(self, padx=32)
        tk.Label(c, text="✓", font=("Segoe UI", 40), fg=SUCCESS,
                 bg=CARD_BG).pack(pady=(16, 4))
        label(c, "Account Created Successfully!",
              size=15, bold=True, color=SUCCESS, anchor="center").pack()
        divider(c)
        rows = [("Account Holder", name), ("Account Number", acc_no),
                ("Opening Balance", f"₹{balance:.2f}")]
        for k, v in rows:
            r = tk.Frame(c, bg=CARD_BG)
            r.pack(fill="x", padx=16, pady=3)
            label(r, k, size=12, color=MUTED).pack(side="left")
            label(r, v, size=12, bold=True).pack(side="right")
        divider(c)
        tk.Label(c, text="⚠  Save your account number safely!",
                 font=("Segoe UI", 11), fg="#B45309", bg=CARD_BG).pack(pady=(0, 12))
        btn(c, "Go to Login", self.app.show_login, color=PRIMARY)
        btn(c, "Go to Home",  self.app.show_home,  color="#64748B")
        tk.Frame(c, bg=CARD_BG, height=8).pack()

# ─────────────────────────────────────────
#  LOGIN SCREEN
# ─────────────────────────────────────────
class LoginScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        topbar(self, "Login", self.app.show_home)
        tk.Frame(self, bg=BG, height=32).pack()

        c = card(self, padx=32)
        tk.Label(c, text="🔒", font=("Segoe UI", 32), bg=CARD_BG).pack(pady=(12, 4))
        label(c, "Login to your account", size=14, bold=True,
              anchor="center").pack(pady=(0, 16))

        label(c, "Account Number").pack(anchor="w", padx=16)
        self.acc_e = entry(c); self.acc_e.pack_configure(padx=16)

        label(c, "PIN").pack(anchor="w", padx=16)
        self.pin_e = entry(c, show="●"); self.pin_e.pack_configure(padx=16)

        tk.Frame(c, bg=CARD_BG, height=4).pack()
        f = tk.Frame(c, bg=CARD_BG)
        f.pack(fill="x", padx=16, pady=(0, 8))
        btn(f, "Login", self._login, full=False)

        tk.Frame(c, bg=CARD_BG, height=4).pack()
        label(c, "Don't have an account?", size=11, color=MUTED,
              anchor="center").pack()
        link_btn(c, "Create one here", self.app.show_create)
        tk.Frame(c, bg=CARD_BG, height=12).pack()

    def _login(self):
        acc_no = self.acc_e.get().strip()
        pin    = self.pin_e.get().strip()
        data   = load_data()
        if acc_no not in data:
            return messagebox.showerror("Error", "Account not found.")
        if data[acc_no]["pin"] != hash_pin(pin):
            return messagebox.showerror("Error", "Incorrect PIN.")
        self.app.show_dashboard(acc_no)

# ─────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────
class DashboardScreen(tk.Frame):
    def __init__(self, app, acc_no):
        super().__init__(app, bg=BG)
        self.app = app
        self.acc_no = acc_no
        self._build()

    def _build(self):
        data = load_data()
        acc  = data.get(self.acc_no, {})

        topbar(self, "Dashboard")

        # Balance hero card
        hero = tk.Frame(self, bg=PRIMARY)
        hero.pack(fill="x")
        tk.Frame(hero, bg=PRIMARY, height=16).pack()
        tk.Label(hero, text=acc.get("name", ""),
                 font=("Segoe UI", 13, "bold"), fg="white", bg=PRIMARY).pack()
        tk.Label(hero, text=f"Acc: {self.acc_no}",
                 font=("Segoe UI", 10), fg="#BFDBFE", bg=PRIMARY).pack(pady=(2, 8))
        tk.Label(hero, text=f"₹{acc.get('balance', 0):,.2f}",
                 font=("Segoe UI", 30, "bold"), fg="white", bg=PRIMARY).pack()
        tk.Label(hero, text="Available Balance",
                 font=("Segoe UI", 10), fg="#BFDBFE", bg=PRIMARY).pack(pady=(2, 16))

        sf = ScrollFrame(self)
        sf.pack(fill="both", expand=True)
        p = sf.inner

        section_title(p, "TRANSACTIONS")

        row1 = tk.Frame(p, bg=BG)
        row1.pack(fill="x", padx=24, pady=(0, 10))
        self._action_card(row1, "💰", "Deposit",   SUCCESS, lambda: self.app.show_deposit(self.acc_no))
        tk.Frame(row1, bg=BG, width=12).pack(side="left")
        self._action_card(row1, "💸", "Withdraw",  DANGER,  lambda: self.app.show_withdraw(self.acc_no))

        row2 = tk.Frame(p, bg=BG)
        row2.pack(fill="x", padx=24, pady=(0, 10))
        self._action_card(row2, "🔄", "Transfer",  PRIMARY, lambda: self.app.show_transfer(self.acc_no))
        tk.Frame(row2, bg=BG, width=12).pack(side="left")
        self._action_card(row2, "📊", "History",   "#7C3AED", lambda: self.app.show_history(self.acc_no))

        section_title(p, "ACCOUNT")

        row3 = tk.Frame(p, bg=BG)
        row3.pack(fill="x", padx=24, pady=(0, 10))
        self._action_card(row3, "👤", "Balance",   "#0891B2", lambda: self.app.show_balance(self.acc_no))
        tk.Frame(row3, bg=BG, width=12).pack(side="left")
        self._action_card(row3, "🚪", "Logout",    MUTED,    self.app.show_home)

        # Delete row (full width)
        del_f = tk.Frame(p, bg=BG)
        del_f.pack(fill="x", padx=24, pady=(0, 24))
        tk.Button(del_f, text="Delete Account", command=lambda: self.app.show_delete(self.acc_no),
                  font=("Segoe UI", 11), fg=DANGER, bg=CARD_BG,
                  relief="flat", cursor="hand2",
                  highlightthickness=1, highlightbackground=DANGER,
                  pady=8).pack(fill="x")

    def _action_card(self, parent, icon, title, color, cmd):
        f = tk.Frame(parent, bg=CARD_BG, relief="flat",
                     highlightthickness=1, highlightbackground=BORDER,
                     cursor="hand2", width=190, height=90)
        f.pack(side="left", fill="both", expand=True)
        f.pack_propagate(False)
        tk.Label(f, text=icon, font=("Segoe UI", 22), bg=CARD_BG).pack(pady=(14, 2))
        tk.Label(f, text=title, font=("Segoe UI", 12, "bold"),
                 fg=color, bg=CARD_BG).pack()
        for w in (f, *f.winfo_children()):
            w.bind("<Button-1>", lambda e, c=cmd: c())

# ─────────────────────────────────────────
#  DEPOSIT SCREEN
# ─────────────────────────────────────────
class DepositScreen(tk.Frame):
    def __init__(self, app, acc_no):
        super().__init__(app, bg=BG)
        self.app = app
        self.acc_no = acc_no
        self._build()

    def _build(self):
        topbar(self, "Deposit Money", lambda: self.app.show_dashboard(self.acc_no))
        tk.Frame(self, bg=BG, height=32).pack()

        data = load_data()
        bal = data[self.acc_no]["balance"]

        c = card(self, padx=32)
        tk.Label(c, text="💰", font=("Segoe UI", 36), bg=CARD_BG).pack(pady=(12, 4))
        label(c, f"Current Balance: ₹{bal:,.2f}",
              size=12, color=MUTED, anchor="center").pack(pady=(0, 16))

        label(c, "Amount to Deposit (₹)").pack(anchor="w", padx=16)
        self.amt_e = entry(c); self.amt_e.pack_configure(padx=16)

        f = tk.Frame(c, bg=CARD_BG)
        f.pack(fill="x", padx=16, pady=(0, 16))
        btn(f, "Deposit", self._deposit, color=SUCCESS, full=False)

    def _deposit(self):
        try:
            amt = float(self.amt_e.get())
            if amt <= 0:
                raise ValueError
        except ValueError:
            return messagebox.showerror("Error", "Enter a valid amount.")
        data = load_data()
        data[self.acc_no]["balance"] += amt
        data[self.acc_no]["transactions"].append({
            "type": "Deposit", "amount": amt,
            "date": get_timestamp(),
            "balance_after": data[self.acc_no]["balance"]
        })
        save_data(data)
        new_bal = data[self.acc_no]["balance"]
        messagebox.showinfo("Success",
            f"₹{amt:,.2f} deposited successfully!\n\nNew Balance: ₹{new_bal:,.2f}")
        self.app.show_dashboard(self.acc_no)

# ─────────────────────────────────────────
#  WITHDRAW SCREEN
# ─────────────────────────────────────────
class WithdrawScreen(tk.Frame):
    def __init__(self, app, acc_no):
        super().__init__(app, bg=BG)
        self.app = app
        self.acc_no = acc_no
        self._build()

    def _build(self):
        topbar(self, "Withdraw Money", lambda: self.app.show_dashboard(self.acc_no))
        tk.Frame(self, bg=BG, height=32).pack()

        data = load_data()
        bal = data[self.acc_no]["balance"]

        c = card(self, padx=32)
        tk.Label(c, text="💸", font=("Segoe UI", 36), bg=CARD_BG).pack(pady=(12, 4))
        label(c, f"Available Balance: ₹{bal:,.2f}",
              size=12, color=MUTED, anchor="center").pack(pady=(0, 16))

        label(c, "Amount to Withdraw (₹)").pack(anchor="w", padx=16)
        self.amt_e = entry(c); self.amt_e.pack_configure(padx=16)

        f = tk.Frame(c, bg=CARD_BG)
        f.pack(fill="x", padx=16, pady=(0, 16))
        btn(f, "Withdraw", self._withdraw, color=DANGER, full=False)

    def _withdraw(self):
        data = load_data()
        bal  = data[self.acc_no]["balance"]
        try:
            amt = float(self.amt_e.get())
            if amt <= 0:
                raise ValueError
        except ValueError:
            return messagebox.showerror("Error", "Enter a valid amount.")
        if amt > bal:
            return messagebox.showerror("Error", "Insufficient balance.")
        if bal - amt < 500:
            return messagebox.showerror("Error",
                "Cannot withdraw. Minimum balance of ₹500 must be maintained.")
        data[self.acc_no]["balance"] -= amt
        data[self.acc_no]["transactions"].append({
            "type": "Withdrawal", "amount": amt,
            "date": get_timestamp(),
            "balance_after": data[self.acc_no]["balance"]
        })
        save_data(data)
        new_bal = data[self.acc_no]["balance"]
        messagebox.showinfo("Success",
            f"₹{amt:,.2f} withdrawn successfully!\n\nRemaining Balance: ₹{new_bal:,.2f}")
        self.app.show_dashboard(self.acc_no)

# ─────────────────────────────────────────
#  TRANSFER SCREEN
# ─────────────────────────────────────────
class TransferScreen(tk.Frame):
    def __init__(self, app, acc_no):
        super().__init__(app, bg=BG)
        self.app = app
        self.acc_no = acc_no
        self._build()

    def _build(self):
        topbar(self, "Transfer Money", lambda: self.app.show_dashboard(self.acc_no))
        tk.Frame(self, bg=BG, height=32).pack()

        data = load_data()
        bal = data[self.acc_no]["balance"]

        c = card(self, padx=32)
        tk.Label(c, text="🔄", font=("Segoe UI", 36), bg=CARD_BG).pack(pady=(12, 4))
        label(c, f"Your Balance: ₹{bal:,.2f}",
              size=12, color=MUTED, anchor="center").pack(pady=(0, 16))

        label(c, "Recipient Account Number").pack(anchor="w", padx=16)
        self.rec_e = entry(c); self.rec_e.pack_configure(padx=16)

        label(c, "Amount (₹)").pack(anchor="w", padx=16)
        self.amt_e = entry(c); self.amt_e.pack_configure(padx=16)

        f = tk.Frame(c, bg=CARD_BG)
        f.pack(fill="x", padx=16, pady=(0, 16))
        btn(f, "Transfer", self._transfer, color=PRIMARY, full=False)

    def _transfer(self):
        target = self.rec_e.get().strip()
        data   = load_data()
        bal    = data[self.acc_no]["balance"]

        if target == self.acc_no:
            return messagebox.showerror("Error", "Cannot transfer to your own account.")
        if target not in data:
            return messagebox.showerror("Error", "Recipient account not found.")
        try:
            amt = float(self.amt_e.get())
            if amt <= 0:
                raise ValueError
        except ValueError:
            return messagebox.showerror("Error", "Enter a valid amount.")
        if amt > bal:
            return messagebox.showerror("Error", "Insufficient balance.")
        if bal - amt < 500:
            return messagebox.showerror("Error",
                "Cannot transfer. Minimum balance of ₹500 must be maintained.")

        rec_name = data[target]["name"]
        ok = messagebox.askyesno("Confirm Transfer",
            f"Transfer ₹{amt:,.2f} to {rec_name}?\n\nAccount: {target}")
        if not ok:
            return

        data[self.acc_no]["balance"] -= amt
        data[self.acc_no]["transactions"].append({
            "type": f"Transfer to {target}", "amount": amt,
            "date": get_timestamp(),
            "balance_after": data[self.acc_no]["balance"]
        })
        data[target]["balance"] += amt
        data[target]["transactions"].append({
            "type": f"Transfer from {self.acc_no}", "amount": amt,
            "date": get_timestamp(),
            "balance_after": data[target]["balance"]
        })
        save_data(data)
        new_bal = data[self.acc_no]["balance"]
        messagebox.showinfo("Success",
            f"₹{amt:,.2f} transferred to {rec_name}!\n\nYour Balance: ₹{new_bal:,.2f}")
        self.app.show_dashboard(self.acc_no)

# ─────────────────────────────────────────
#  BALANCE SCREEN
# ─────────────────────────────────────────
class BalanceScreen(tk.Frame):
    def __init__(self, app, acc_no):
        super().__init__(app, bg=BG)
        self.app = app
        self.acc_no = acc_no
        self._build()

    def _build(self):
        topbar(self, "Account Balance", lambda: self.app.show_dashboard(self.acc_no))
        tk.Frame(self, bg=BG, height=32).pack()

        data = load_data()
        acc  = data[self.acc_no]

        c = card(self, padx=32)
        tk.Label(c, text="👤", font=("Segoe UI", 36), bg=CARD_BG).pack(pady=(16, 8))

        rows = [
            ("Account Holder", acc["name"]),
            ("Account Number", self.acc_no),
            ("Phone",          acc.get("phone", "-")),
            ("Balance",        f"₹{acc['balance']:,.2f}"),
            ("Account Since",  acc.get("created_on", "-")),
        ]
        for k, v in rows:
            r = tk.Frame(c, bg=CARD_BG)
            r.pack(fill="x", padx=16, pady=5)
            label(r, k, size=12, color=MUTED).pack(side="left")
            lbl = label(r, v, size=12, bold=True)
            if k == "Balance":
                lbl.config(fg=SUCCESS)
            lbl.pack(side="right")
            tk.Frame(c, bg=BORDER, height=1).pack(fill="x", padx=16)

        tk.Frame(c, bg=CARD_BG, height=8).pack()

# ─────────────────────────────────────────
#  TRANSACTION HISTORY SCREEN
# ─────────────────────────────────────────
class HistoryScreen(tk.Frame):
    def __init__(self, app, acc_no):
        super().__init__(app, bg=BG)
        self.app = app
        self.acc_no = acc_no
        self._build()

    def _build(self):
        topbar(self, "Transaction History", lambda: self.app.show_dashboard(self.acc_no))

        data = load_data()
        txns = data[self.acc_no]["transactions"][-10:][::-1]

        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=16, pady=12)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                         background=WHITE, fieldbackground=WHITE,
                         foreground=TEXT, rowheight=36,
                         font=("Segoe UI", 11))
        style.configure("Custom.Treeview.Heading",
                         background=PRIMARY, foreground="white",
                         font=("Segoe UI", 11, "bold"), relief="flat")
        style.map("Custom.Treeview", background=[("selected", "#DBEAFE")])

        cols = ("#", "Type", "Amount", "Balance", "Date")
        tree = ttk.Treeview(container, columns=cols, show="headings",
                             style="Custom.Treeview", height=14)

        widths = [30, 180, 80, 80, 145]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center" if col != "Type" else "w")

        for i, t in enumerate(txns, 1):
            amt   = f"₹{t['amount']:,.2f}"
            bal   = f"₹{t['balance_after']:,.2f}"
            tags  = ("deposit",) if "Deposit" in t["type"] or "Transfer from" in t["type"] else ("withdraw",)
            tree.insert("", "end", values=(i, t["type"], amt, bal, t["date"]), tags=tags)

        tree.tag_configure("deposit",  foreground=SUCCESS)
        tree.tag_configure("withdraw", foreground=DANGER)

        sb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        if not txns:
            tk.Label(self, text="No transactions found.",
                     font=("Segoe UI", 13), fg=MUTED, bg=BG).pack(pady=40)

# ─────────────────────────────────────────
#  DELETE ACCOUNT SCREEN
# ─────────────────────────────────────────
class DeleteScreen(tk.Frame):
    def __init__(self, app, acc_no):
        super().__init__(app, bg=BG)
        self.app = app
        self.acc_no = acc_no
        self._build()

    def _build(self):
        topbar(self, "Delete Account", lambda: self.app.show_dashboard(self.acc_no))
        tk.Frame(self, bg=BG, height=32).pack()

        c = card(self, padx=32)
        tk.Label(c, text="⚠️", font=("Segoe UI", 36), bg=CARD_BG).pack(pady=(16, 4))
        label(c, "Delete Account", size=16, bold=True,
              color=DANGER, anchor="center").pack()
        label(c, "This action is permanent and cannot be undone.",
              size=11, color=MUTED, anchor="center").pack(pady=(4, 16))

        label(c, "Enter your PIN to confirm").pack(anchor="w", padx=16)
        self.pin_e = entry(c, show="●"); self.pin_e.pack_configure(padx=16)

        f = tk.Frame(c, bg=CARD_BG)
        f.pack(fill="x", padx=16, pady=(0, 16))
        btn(f, "Delete My Account", self._delete, color=DANGER, full=False)

    def _delete(self):
        pin  = self.pin_e.get().strip()
        data = load_data()
        if data[self.acc_no]["pin"] != hash_pin(pin):
            return messagebox.showerror("Error", "Incorrect PIN.")
        ok = messagebox.askyesno("Final Confirmation",
            "Are you absolutely sure you want to delete your account?\n"
            "All your data will be permanently lost.")
        if not ok:
            return
        name = data[self.acc_no]["name"]
        del data[self.acc_no]
        save_data(data)
        messagebox.showinfo("Account Deleted",
            f"Account for '{name}' has been permanently deleted.")
        self.app.show_home()

# ─────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────
if __name__ == "__main__":
    app = BankApp()
    app.mainloop()