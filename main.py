import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from security_config import PACKAGES, SECURITY_OPTIONS, DESKTOP_OPTIONS, GUI_PACKAGES
from config_generator import generate_config

BG_COLOR = "#1e1e2e"       
FG_COLOR = "#cdd6f4"       
ACCENT_COLOR = "#89b4fa"   
SECONDARY_BG = "#313244"   
BUTTON_BG = "#45475a"      
BUTTON_ACTIVE_BG = "#6c7086"
FRAME_BG = "#181825"       
TEXT_BG = "#1e1e2e"        

class NixConfigGeneratorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Генератор конфигураций NixOS")
        self.root.geometry("1280x800")
        self.root.configure(bg=BG_COLOR)

        self.hostname_var = tk.StringVar(value="nixos")
        self.timezone_var = tk.StringVar(value="Asia/Vladivostok")
        self.username_var = tk.StringVar(value="user")
        self.user_desc_var = tk.StringVar(value="Основной пользователь")
        self.state_version_var = tk.StringVar(value="26.05")
        self.password_var = tk.StringVar()
        self.desktop_var = tk.StringVar(value="Без графики (Minimal)")

        self.tcp_ports_var = tk.StringVar(value="22 80 443")
        self.udp_ports_var = tk.StringVar(value="53 123")
        self.bantime_var = tk.StringVar(value="1h")
        self.findtime_var = tk.StringVar(value="10m")

        self.security_vars: dict[str, tk.BooleanVar] = {}
        self.package_vars: dict[str, tk.BooleanVar] = {}
        self.gui_package_vars: dict[str, tk.BooleanVar] = {}
        self.gui_pkg_widgets: list[ttk.Checkbutton] = []

        self._setup_styles()
        self._create_widgets()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background=BG_COLOR, foreground=FG_COLOR)
        style.configure("TFrame", background=FRAME_BG)
        style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR)
        style.configure("TLabelframe", background=FRAME_BG, foreground=FG_COLOR, borderwidth=2, relief="groove")
        style.configure("TLabelframe.Label", background=FRAME_BG, foreground=ACCENT_COLOR, font=("Segoe UI", 10, "bold"))

        style.configure("TEntry", fieldbackground=SECONDARY_BG, foreground=FG_COLOR, borderwidth=1, focusthickness=0)
        style.map("TEntry", fieldbackground=[("focus", BUTTON_ACTIVE_BG)])

        style.configure("TButton", background=BUTTON_BG, foreground=FG_COLOR, borderwidth=0, focusthickness=0, padding=6)
        style.map("TButton", background=[("active", BUTTON_ACTIVE_BG), ("pressed", ACCENT_COLOR)])

        style.configure("TCheckbutton", background=BG_COLOR, foreground=FG_COLOR)
        style.map("TCheckbutton", background=[("active", BG_COLOR)], foreground=[("active", ACCENT_COLOR)])
        style.configure("TRadiobutton", background=BG_COLOR, foreground=FG_COLOR)
        style.map("TRadiobutton", background=[("active", BG_COLOR)], foreground=[("active", ACCENT_COLOR)])

        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", background=BUTTON_BG, foreground=FG_COLOR, padding=[10, 4])
        style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)], foreground=[("selected", BG_COLOR)])

        style.configure("TScrollbar", background=BUTTON_BG, troughcolor=BG_COLOR, arrowcolor=FG_COLOR)
        style.map("TScrollbar", background=[("active", BUTTON_ACTIVE_BG)])

        style.configure("TCombobox", fieldbackground=SECONDARY_BG, foreground=FG_COLOR)
        style.map("TCombobox", fieldbackground=[("readonly", SECONDARY_BG)], foreground=[("readonly", FG_COLOR)])

    def _create_widgets(self):
        self.canvas = tk.Canvas(self.root, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self._canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        basic = ttk.LabelFrame(self.scrollable_frame, text="Основные настройки системы", padding=10)
        basic.pack(fill="x", padx=15, pady=8)

        fields = [
            ("Имя хоста:", self.hostname_var),
            ("Часовой пояс:", self.timezone_var),
            ("Имя пользователя:", self.username_var),
            ("Описание пользователя:", self.user_desc_var),
        ]
        for i, (label, var) in enumerate(fields):
            ttk.Label(basic, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=4)
            ttk.Entry(basic, textvariable=var, width=35).grid(row=i, column=1, sticky="w", pady=4)

        ttk.Label(basic, text="Пароль (пусто — без пароля):").grid(row=4, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(basic, textvariable=self.password_var, width=35, show="*").grid(row=4, column=1, sticky="w", pady=4)

        ttk.Label(basic, text="stateVersion:").grid(row=5, column=0, sticky="w", padx=5, pady=4)
        ttk.Combobox(
            basic,
            textvariable=self.state_version_var,
            values=["26.05", "25.11", "25.05"],
            state="readonly",
            width=33,
        ).grid(row=5, column=1, sticky="w", pady=4)

        pkg_frame = ttk.LabelFrame(self.scrollable_frame, text="Пакеты", padding=10)
        pkg_frame.pack(fill="x", padx=15, pady=8)
        notebook = ttk.Notebook(pkg_frame)
        notebook.pack(fill="x", expand=True)

        for category, packages in PACKAGES.items():
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=category)
            for i, pkg in enumerate(packages):
                var = tk.BooleanVar()
                self.package_vars[pkg] = var
                ttk.Checkbutton(tab, text=pkg, variable=var).grid(
                    row=i // 3, column=i % 3, sticky="w", padx=6, pady=3
                )

        custom_tab = ttk.Frame(notebook)
        notebook.add(custom_tab, text="Custom")
        self.custom_packages_text = scrolledtext.ScrolledText(custom_tab, height=6, bg=SECONDARY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, relief="flat")
        self.custom_packages_text.pack(fill="both", expand=True, padx=4, pady=4)
        self.custom_packages_text.insert(tk.END, "# Один пакет на строку\n")

        de_frame = ttk.LabelFrame(self.scrollable_frame, text="Графическая оболочка", padding=10)
        de_frame.pack(fill="x", padx=15, pady=8)

        for i, de_name in enumerate(DESKTOP_OPTIONS.keys()):
            ttk.Radiobutton(
                de_frame,
                text=de_name,
                variable=self.desktop_var,
                value=de_name,
                command=self._on_desktop_changed,
            ).grid(row=i // 3, column=i % 3, sticky="w", padx=6, pady=2)

        self.gui_pkg_frame = ttk.LabelFrame(
            self.scrollable_frame, text="Графические приложения (только с DE)", padding=10
        )
        self.gui_pkg_frame.pack(fill="x", padx=15, pady=8)

        gui_notebook = ttk.Notebook(self.gui_pkg_frame)
        gui_notebook.pack(fill="x", expand=True)

        for category, packages in GUI_PACKAGES.items():
            tab = ttk.Frame(gui_notebook)
            gui_notebook.add(tab, text=category)
            for i, pkg in enumerate(packages):
                var = tk.BooleanVar()
                self.gui_package_vars[pkg] = var
                cb = ttk.Checkbutton(tab, text=pkg, variable=var, state="disabled")
                cb.grid(row=i // 3, column=i % 3, sticky="w", padx=6, pady=3)
                self.gui_pkg_widgets.append(cb)

        extra = ttk.LabelFrame(self.scrollable_frame, text="Настройки Firewall и Fail2ban", padding=10)
        extra.pack(fill="x", padx=15, pady=8)

        extra_fields = [
            ("Разрешённые TCP порты (через пробел):", self.tcp_ports_var),
            ("Разрешённые UDP порты (через пробел):", self.udp_ports_var),
            ("Fail2ban bantime (пример: 1h, 3600):", self.bantime_var),
            ("Fail2ban findtime (пример: 10m, 600):", self.findtime_var),
        ]
        for i, (label, var) in enumerate(extra_fields):
            ttk.Label(extra, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=4)
            ttk.Entry(extra, textvariable=var, width=35).grid(row=i, column=1, sticky="w", pady=4)

        sec_frame = ttk.LabelFrame(self.scrollable_frame, text="Опции безопасности", padding=10)
        sec_frame.pack(fill="x", padx=15, pady=8)

        for idx, option in enumerate(SECURITY_OPTIONS.keys()):
            var = tk.BooleanVar()
            self.security_vars[option] = var
            ttk.Checkbutton(sec_frame, text=option, variable=var).grid(
                row=idx // 2, column=idx % 2, sticky="w", padx=8, pady=3
            )

        ssh_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Публичные ключи SSH (обязательно при «SSH только с ключами»)",
            padding=10,
        )
        ssh_frame.pack(fill="x", padx=15, pady=8)
        self.ssh_key_text = scrolledtext.ScrolledText(ssh_frame, height=5, bg=SECONDARY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, relief="flat")
        self.ssh_key_text.pack(fill="both", expand=True)
        self.ssh_key_text.insert(tk.END, "# Вставьте публичные ключи, каждый с новой строки\n")

        action_frame = ttk.Frame(self.scrollable_frame)
        action_frame.pack(fill="x", padx=15, pady=10)
        for text, cmd in [
            ("Сгенерировать", self._generate_and_show),
            ("Сохранить", self._save_to_file),
            ("Загрузить", self._load_from_file),
            ("Очистить", self._clear_form),
        ]:
            btn = ttk.Button(action_frame, text=text, command=cmd)
            btn.pack(side="left", padx=6)

        # --- Результат ---
        self.result_text = scrolledtext.ScrolledText(
            self.scrollable_frame, height=22,
            bg=TEXT_BG, fg=FG_COLOR, insertbackground=FG_COLOR,
            font=("Consolas", 10), relief="flat", wrap=tk.WORD
        )
        self.result_text.pack(fill="both", expand=True, padx=15, pady=8)

    def _on_desktop_changed(self):
        is_gui = self.desktop_var.get() != "Без графики (Minimal)"
        state = "normal" if is_gui else "disabled"
        for cb in self.gui_pkg_widgets:
            cb.configure(state=state)
        if not is_gui:
            for v in self.gui_package_vars.values():
                v.set(False)

    def _on_frame_configure(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self._canvas_window, width=event.width)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def _get_ssh_keys(self) -> list[str]:
        return [
            line.strip()
            for line in self.ssh_key_text.get("1.0", tk.END).splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    def _get_all_packages(self) -> list[str]:
        packages = [pkg for pkg, var in self.package_vars.items() if var.get()]
        packages += [pkg for pkg, var in self.gui_package_vars.items() if var.get()]
        for line in self.custom_packages_text.get("1.0", tk.END).splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                packages.append(line)
        return list(dict.fromkeys(packages))

    @staticmethod
    def _parse_ports(ports_str: str) -> list[int]:
        ports = []
        for part in ports_str.replace(",", " ").split():
            if part.isdigit():
                port = int(part)
                if 1 <= port <= 65535:
                    ports.append(port)
        return list(dict.fromkeys(ports))

    def _generate_and_show(self):
        security_options = [opt for opt, var in self.security_vars.items() if var.get()]
        ssh_keys = self._get_ssh_keys()
        password = self.password_var.get().strip()

        if "SSH только с ключами" in security_options and not ssh_keys:
            messagebox.showerror(
                "Ошибка",
                "«SSH только с ключами» отключает вход по паролю, но SSH-ключ не добавлен.\n"
                "Добавьте ключ или отключите опцию.",
            )
            return

        if not password and not ssh_keys:
            if not messagebox.askyesno(
                "Внимание",
                "Пароль не задан и SSH-ключи не добавлены.\n"
                "Войти в систему удалённо будет невозможно.\n\n"
                "Продолжить? (рекомендуется задать пароль или добавить SSH-ключ)",
            ):
                return

        tcp_ports = self._parse_ports(self.tcp_ports_var.get())
        udp_ports = self._parse_ports(self.udp_ports_var.get())

        if "Firewall" in security_options and 22 not in tcp_ports:
            tcp_ports.insert(0, 22)
            self.tcp_ports_var.set(" ".join(str(p) for p in tcp_ports))

        hostname = self.hostname_var.get().strip()
        username = self.username_var.get().strip()
        if not hostname or not username:
            messagebox.showerror("Ошибка", "Имя хоста и имя пользователя обязательны.")
            return

        data = {
            "hostname": hostname,
            "timezone": self.timezone_var.get().strip(),
            "username": username,
            "user_description": self.user_desc_var.get().strip(),
            "state_version": self.state_version_var.get().strip(),
            "packages": self._get_all_packages(),
            "security_options": security_options,
            "desktop": self.desktop_var.get(),
            "ssh_keys": ssh_keys,
            "tcp_ports": tcp_ports,
            "udp_ports": udp_ports,
            "bantime": self.bantime_var.get().strip() or "1h",
            "findtime": self.findtime_var.get().strip() or "10m",
            "password": password,
        }

        try:
            config_content = generate_config(data)
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, config_content)
            messagebox.showinfo("Готово", "Конфигурация успешно сгенерирована.")
        except Exception as exc:
            messagebox.showerror("Ошибка генерации", str(exc))

    def _save_to_file(self):
        content = self.result_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Нет данных", "Сначала сгенерируйте конфигурацию.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".nix",
            filetypes=[("Nix files", "*.nix"), ("All files", "*.*")],
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    def _load_from_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Nix files", "*.nix"), ("All files", "*.*")]
        )
        if path:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, content)

    def _clear_form(self):
        self.hostname_var.set("nixos")
        self.timezone_var.set("Asia/Vladivostok")
        self.username_var.set("user")
        self.user_desc_var.set("Основной пользователь")
        self.state_version_var.set("26.05")
        self.password_var.set("")
        self.tcp_ports_var.set("22 80 443")
        self.udp_ports_var.set("53 123")
        self.bantime_var.set("1h")
        self.findtime_var.set("10m")
        self.desktop_var.set("Без графики (Minimal)")
        self._on_desktop_changed()
        for v in self.package_vars.values():
            v.set(False)
        for v in self.security_vars.values():
            v.set(False)
        self.custom_packages_text.delete("1.0", tk.END)
        self.custom_packages_text.insert(tk.END, "# Один пакет на строку\n")
        self.ssh_key_text.delete("1.0", tk.END)
        self.ssh_key_text.insert(tk.END, "# Вставьте публичные ключи, каждый с новой строки\n")
        self.result_text.delete("1.0", tk.END)

def main():
    root = tk.Tk()
    NixConfigGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
