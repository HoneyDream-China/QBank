import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
import re
from datetime import datetime

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("单机刷题系统 - 智能模拟多用户版")
        self.root.geometry("1150x650")
        self.root.resizable(False, False)
        
        # 核心配置文件名（增加默认和用户凭证）
        self.u_file = "users_db.json"
        self.q_file = ""  # 动态选择的题库文件名
        
        # 加载用户凭证库
        self.users_db = self.load_json(self.u_file, {})
        self.all_questions = [] # 动态加载的公共题库
        
        # 初始进入登录页面
        self.show_login_page()

    def load_json(self, filename, default_val):
        """通用安全加载 JSON 文件"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"读取 {filename} 失败: {e}")
                return default_val
        return default_val

    # ==================== 登录/注册模块 ====================
    def show_login_page(self):
        """构建现代简约的登录/注册界面"""
        for w in self.root.winfo_children(): w.destroy()
        
        self.login_frame = tk.Frame(self.root, bg="#F5F5F5")
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(self.login_frame, text="宝宝定制刷题系统", font=("Microsoft YaHei", 20, "bold"), bg="#F5F5F5", fg="#1976D2").grid(row=0, column=0, columnspan=2, pady=(0, 25))
        
        tk.Label(self.login_frame, text="账号 (11位以内数字):", font=("Microsoft YaHei", 11), bg="#F5F5F5").grid(row=1, column=0, sticky=tk.E, pady=10, padx=5)
        self.ent_user = tk.Entry(self.login_frame, font=("Microsoft YaHei", 11), width=25)
        self.ent_user.grid(row=1, column=1, pady=10, padx=5)
        
        tk.Label(self.login_frame, text="密码 (字母/数字/@/.):", font=("Microsoft YaHei", 11), bg="#F5F5F5").grid(row=2, column=0, sticky=tk.E, pady=10, padx=5)
        self.ent_pwd = tk.Entry(self.login_frame, font=("Microsoft YaHei", 11), width=25, show="*")
        self.ent_pwd.grid(row=2, column=1, pady=10, padx=5)
        
        btn_login = tk.Button(self.login_frame, text="安全登录", font=("Microsoft YaHei", 11, "bold"), width=10, bg="#2196F3", fg="white", relief=tk.FLAT, command=self.handle_login)
        btn_login.grid(row=3, column=0, pady=25, padx=5)
        
        btn_reg = tk.Button(self.login_frame, text="账号注册", font=("Microsoft YaHei", 11), width=10, bg="#4CAF50", fg="white", relief=tk.FLAT, command=self.handle_register)
        btn_reg.grid(row=3, column=1, pady=25, padx=5)

    def validate_inputs(self, user, pwd):
        """严格正则匹配：账号限11位以内纯数字，密码限数字、英文字母、@、."""
        if not re.match(r"^\d{1,11}$", user):
            messagebox.showerror("格式错误", "账号必须为 11 位以内的纯数字！")
            return False
        if not re.match(r"^[A-Za-z0-9@.]+$", pwd):
            messagebox.showerror("格式错误", "密码仅限数字、大小写英文字母和 '@'、'.' 字符！")
            return False
        return True

    def handle_register(self):
        user = self.ent_user.get().strip()
        pwd = self.ent_pwd.get().strip()
        if not self.validate_inputs(user, pwd): return
        
        if user in self.users_db:
            messagebox.showerror("注册失败", "该账号已被注册！")
            return
            
        self.users_db[user] = pwd
        with open(self.u_file, 'w', encoding='utf-8') as f:
            json.dump(self.users_db, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("注册成功", "恭喜，账号注册成功！现在可以直接点击登录。")

    def handle_login(self):
        user = self.ent_user.get().strip()
        pwd = self.ent_pwd.get().strip()
        if not self.validate_inputs(user, pwd): return
        
        if user not in self.users_db or self.users_db[user] != pwd:
            messagebox.showerror("登录失败", "账号或密码输入错误！")
            return
            
        # 登录成功，绑定当前用户身份，跳转到题库选择界面
        self.current_user = user
        self.login_frame.destroy()
        self.show_bank_selection_page()

    # ==================== 题库选择模块 (新增) ====================
    def show_bank_selection_page(self):
        """构建题库选择界面，自动扫描当前目录下的 JSON 题库"""
        # 获取当前目录下所有的 JSON 文件，排除用户凭证和进度文件
        all_files = os.listdir('.')
        json_banks = [f for f in all_files if f.endswith('.json') and not f.startswith('progress_') and not f.startswith('wrong_questions_') and f != 'users_db.json']
        
        self.bank_frame = tk.Frame(self.root, bg="#F5F5F5")
        self.bank_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(self.bank_frame, text="请选择要挑战的题库", font=("Microsoft YaHei", 18, "bold"), bg="#F5F5F5", fg="#2E7D32").pack(pady=(0, 20))
        
        if not json_banks:
            tk.Label(self.bank_frame, text="⚠ 未在当前目录下检测到有效的题库文件！\n请放入题库 JSON 文件后再试。", font=("Microsoft YaHei", 12), bg="#F5F5F5", fg="red").pack(pady=10)
            btn_back = tk.Button(self.bank_frame, text="返回登录", font=("Microsoft YaHei", 11), bg="#9E9E9E", fg="white", relief=tk.FLAT, command=self.show_login_page)
            btn_back.pack(pady=10)
            return

        # 使用 Combobox 下拉框供用户选择
        tk.Label(self.bank_frame, text="可用题库列表:", font=("Microsoft YaHei", 11), bg="#F5F5F5").pack(anchor=tk.W, pady=5)
        self.bank_combo = ttk.Combobox(self.bank_frame, values=json_banks, font=("Microsoft YaHei", 11), width=35, state="readonly")
        self.bank_combo.pack(pady=10)
        self.bank_combo.current(0) # 默认选中第一个
        
        btn_start = tk.Button(self.bank_frame, text="开始刷题", font=("Microsoft YaHei", 12, "bold"), width=15, bg="#4CAF50", fg="white", relief=tk.FLAT, command=self.handle_bank_selection)
        btn_start.pack(pady=20)

    def handle_bank_selection(self):
        selected_bank = self.bank_combo.get()
        if not selected_bank:
            messagebox.showwarning("提示", "请先选择一个题库！")
            return
            
        # 加载选中的题库
        self.q_file = selected_bank
        self.all_questions = self.load_json(self.q_file, [])
        
        if not self.all_questions:
            messagebox.showerror("加载失败", f"题库 {selected_bank} 为空或解析失败！")
            return
            
        # 题库加载成功，移除选择界面，初始化用户数据
        self.bank_frame.destroy()
        self.initialize_user_data()

    # ==================== 数据初始化 ====================
    def initialize_user_data(self):
        """专人专档：加载属于该用户、该题库的独立错题本与刷题日志"""
        # 获取不含后缀的题库名，用于区分不同题库的进度
        bank_name = os.path.splitext(self.q_file)[0]
        
        # 进度文件名升级为：progress_用户名_题库名.json
        self.p_file = f"progress_{self.current_user}_{bank_name}.json"
        self.w_file = f"wrong_questions_{self.current_user}_{bank_name}.json"
        
        self.wrong_questions = self.load_json(self.w_file, [])
        self.progress = self.load_json(self.p_file, {
            "seq_idx": 0,
            "history": {},
            "resolved_wrong_keys": [],
            "random_records": []  
        })
        
        if "history" not in self.progress: self.progress["history"] = {}
        if "resolved_wrong_keys" not in self.progress: self.progress["resolved_wrong_keys"] = []
        if "random_records" not in self.progress: self.progress["random_records"] = []
        
        # 启动自净化错题逻辑
        self.resolved_wrong_keys = set(self.progress["resolved_wrong_keys"])
        if self.resolved_wrong_keys:
            self.wrong_questions = [q for q in self.wrong_questions if self.get_q_key(q) not in self.resolved_wrong_keys]
            self.resolved_wrong_keys.clear()
            self.progress["resolved_wrong_keys"] = []
            
        self.current_mode = "seq"
        self.current_list = self.all_questions
        self.current_idx = self.progress.get("seq_idx", 0)
        self.has_answered = False
        
        # 独立运行期状态变量
        self.random_choices = {}   
        self.random_history = {}   
        self.random_submitted = False
        self.wrong_history = {}    
        self.current_selected = [] 
        self.sheet_buttons = []
        
        self.build_ui()
        self.init_answer_sheet()
        self.load_question()

    def save_state(self):
        """静默异步保存个人账户进度数据"""
        try:
            self.progress["resolved_wrong_keys"] = list(self.resolved_wrong_keys)
            with open(self.p_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, ensure_ascii=False, indent=2)
            with open(self.w_file, 'w', encoding='utf-8') as f:
                json.dump(self.wrong_questions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"数据隔离保存失败: {e}")

    def get_q_key(self, q):
        return str(q.get('id', q.get('question', '')))

    # ==================== 主系统 UI 构建 ====================
    def build_ui(self):
        """重组主答题工作台界面"""
        # ================= 顶部栏 =================
        self.top_frame = tk.Frame(self.root, bg="#e0e0e0", pady=10, padx=15)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.lbl_stats = tk.Label(self.top_frame, text="", bg="#e0e0e0", font=("Microsoft YaHei", 10, "bold"), fg="#333333")
        self.lbl_stats.pack(side=tk.LEFT)
        
        # 新增：“切换题库”按钮
        btn_switch = tk.Button(self.top_frame, text="🔄 切换题库", command=self.switch_bank, relief=tk.FLAT, bg="#FFE0B2", fg="#E65100", font=("Microsoft YaHei", 9, "bold"))
        btn_switch.pack(side=tk.RIGHT, padx=5)

        btn_hist = tk.Button(self.top_frame, text="📊 随机记录", command=self.show_random_history_window, relief=tk.FLAT, bg="#E0F7FA", fg="#006064", font=("Microsoft YaHei", 9, "bold"))
        btn_hist.pack(side=tk.RIGHT, padx=5)
        btn_wrg = tk.Button(self.top_frame, text="📓 错题本", command=lambda: self.change_mode('wrong'), relief=tk.FLAT, bg="#FFCDD2")
        btn_wrg.pack(side=tk.RIGHT, padx=5)
        btn_rnd = tk.Button(self.top_frame, text="🔀 随机刷题(20题)", command=lambda: self.change_mode('random'), relief=tk.FLAT, bg="#C8E6C9")
        btn_rnd.pack(side=tk.RIGHT, padx=5)
        btn_seq = tk.Button(self.top_frame, text="▶ 顺序刷题", command=lambda: self.change_mode('seq'), relief=tk.FLAT, bg="#BBDEFB")
        btn_seq.pack(side=tk.RIGHT, padx=5)

        # ================= 底部控制栏 =================
        self.bottom_frame = tk.Frame(self.root, bg="#f5f5f5", pady=10, padx=20)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.btn_prev = tk.Button(self.bottom_frame, text="← 上一题", font=("Microsoft YaHei", 11), command=self.prev_q, width=12)
        self.btn_prev.pack(side=tk.LEFT)
        
        self.btn_submit = tk.Button(self.bottom_frame, text="确定答案", font=("Microsoft YaHei", 11, "bold"), command=self.handle_submit_action, width=15, bg="#2196F3", fg="white", relief=tk.FLAT)
        self.btn_submit.pack(side=tk.LEFT, padx=20)
        
        self.btn_next = tk.Button(self.bottom_frame, text="下一题 →", font=("Microsoft YaHei", 11), command=self.next_q, width=12)
        self.btn_next.pack(side=tk.RIGHT)

        # ================= 中间核心区分栏 =================
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 左侧滚动面板
        self.canvas_frame = tk.Frame(self.main_container)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, padx=20, pady=20)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=780)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.lbl_question = tk.Label(self.scrollable_frame, text="", font=("Microsoft YaHei", 14, "bold"), wraplength=730, justify=tk.LEFT)
        self.lbl_question.pack(anchor=tk.W, pady=(0, 15))
        
        # 选项挂载容器
        self.options_frame = tk.Frame(self.scrollable_frame)
        self.options_frame.pack(fill=tk.X, anchor=tk.W)
        
        # 解析展示板
        self.analysis_frame = tk.Frame(self.scrollable_frame, bg="#FFF9C4", padx=10, pady=10)
        self.lbl_analysis = tk.Label(self.analysis_frame, text="", font=("Microsoft YaHei", 11), wraplength=710, justify=tk.LEFT, bg="#FFF9C4", fg="#333")
        self.lbl_analysis.pack(anchor=tk.W)

        # 右侧矩阵答题卡
        self.right_frame = tk.LabelFrame(self.main_container, text=" 答题卡 ", font=("Microsoft YaHei", 11, "bold"), padx=5, pady=5, width=310)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        self.right_frame.pack_propagate(False) 
        
        self.sheet_canvas = tk.Canvas(self.right_frame, highlightthickness=0, width=280)
        self.sheet_scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.sheet_canvas.yview)
        self.sheet_inner_frame = tk.Frame(self.sheet_canvas)
        
        self.sheet_inner_frame.bind("<Configure>", lambda e: self.sheet_canvas.configure(scrollregion=self.sheet_canvas.bbox("all")))
        self.sheet_canvas.create_window((0, 0), window=self.sheet_inner_frame, anchor="nw")
        self.sheet_canvas.configure(yscrollcommand=self.sheet_scrollbar.set)
        
        self.sheet_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sheet_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.root.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def on_mouse_wheel(self, event):
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        if widget and str(self.right_frame) in str(widget):
            self.sheet_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def init_answer_sheet(self):
        """动态绘制全功能响应式答题卡矩阵"""
        for widget in self.sheet_inner_frame.winfo_children(): widget.destroy()
        self.sheet_buttons = []
        
        for i, q in enumerate(self.current_list):
            btn = tk.Button(self.sheet_inner_frame, text=str(i+1), width=4, height=1,
                            font=("Microsoft YaHei", 9), relief=tk.FLAT,
                            command=lambda idx=i: self.jump_to_question(idx))
            row = i // 6
            col = i % 6
            btn.grid(row=row, column=col, padx=4, pady=4)
            self.sheet_buttons.append(btn)

    def update_answer_sheet_colors(self):
        """实时渲染答题卡各坑位的对错/进度色彩状态"""
        for i, q in enumerate(self.current_list):
            if i >= len(self.sheet_buttons): break
            q_key = self.get_q_key(q)
            
            if self.current_mode == 'random':
                if self.random_submitted:
                    item = self.random_history.get(q_key)
                    bg = "#A5D6A7" if item and item.get('status') == "correct" else "#EF9A9A"
                else:
                    bg = "#FFE082" if q_key in self.random_choices and self.random_choices[q_key] else "#E0E0E0"
            else:
                history_item = self.wrong_history.get(q_key) if self.current_mode == 'wrong' else self.progress['history'].get(q_key)
                bg = "#A5D6A7" if history_item and history_item.get('status') == "correct" else ("#EF9A9A" if history_item else "#E0E0E0")
                
            if i == self.current_idx:
                fg = "#0D47A1"  
                font = ("Microsoft YaHei", 9, "bold")
                if (self.current_mode == 'random' and not self.random_submitted) or (self.current_mode != 'random' and not history_item): 
                    bg = "#BBDEFB" 
            else:
                fg = "#333333"
                font = ("Microsoft YaHei", 9)
                
            self.sheet_buttons[i].config(bg=bg, fg=fg, font=font)

    def jump_to_question(self, idx):
        if 0 <= idx < len(self.current_list):
            self.current_idx = idx
            if self.current_mode == 'seq':
                self.progress['seq_idx'] = self.current_idx
                self.save_state()
            self.load_question()

    # ==================== 选项绘制与重构核心 ====================
    def load_question(self):
        """横条一体化渲染与状态判定"""
        if self.current_idx >= len(self.current_list): self.current_idx = 0
        self.canvas.yview_moveto(0) 
        
        for widget in self.options_frame.winfo_children(): widget.destroy()
            
        q = self.current_list[self.current_idx]
        q_key = self.get_q_key(q)
        is_multi = isinstance(q['answer'], list)
        
        if self.current_mode != 'random': self.current_selected = []
        
        q_type = "【多选题】" if is_multi else "【单选/判断】"
        self.lbl_question.config(text=f"第 {self.current_idx + 1} / {len(self.current_list)} 题  {q_type}\n{q['question']}")
        
        self.option_widgets = []
        for i, opt in enumerate(q['options']):
            btn = tk.Button(self.options_frame, text=f" {chr(65+i)}.  {opt}", font=("Microsoft YaHei", 11),
                            relief=tk.FLAT, anchor="w", padx=20, pady=12, bd=0, bg="#F5F5F5", fg="#333333",
                            activebackground="#E0E0E0", justify=tk.LEFT, wraplength=720,
                            command=lambda idx=i: self.click_option_bar(idx))
            btn.pack(fill=tk.X, pady=6)
            self.option_widgets.append(btn)
            
        has_history = False
        is_correct = False
        if self.current_mode == 'random':
            if self.random_submitted:
                has_history = True
                is_correct = self.random_history.get(q_key, {}).get('status') == 'correct'
        else:
            hist_source = self.wrong_history if self.current_mode == 'wrong' else self.progress['history']
            if q_key in hist_source:
                has_history = True
                is_correct = hist_source[q_key].get('status') == 'correct'
                
        if has_history:
            self.has_answered = True
            self.show_analysis(q, q['answer'], is_correct)
        else:
            self.has_answered = False
            self.analysis_frame.pack_forget()
            
        self.refresh_option_bar_colors()
        self.update_submit_button_text(has_history)
        self.update_stats_ui()
        self.update_answer_sheet_colors()

    def update_submit_button_text(self, has_history):
        if self.current_mode == 'random':
            if self.random_submitted:
                self.btn_submit.config(text="试卷已提交", state=tk.DISABLED, bg="#9E9E9E")
            else:
                self.btn_submit.config(text=" 🛑 提交试卷", state=tk.NORMAL, bg="#E53935")
        else:
            if has_history:
                self.btn_submit.config(text="本题已锁定", state=tk.DISABLED, bg="#9E9E9E")
            else:
                self.btn_submit.config(text=" ✔ 确定答案", state=tk.NORMAL, bg="#2196F3")

    def click_option_bar(self, idx):
        q = self.current_list[self.current_idx]
        q_key = self.get_q_key(q)
        is_multi = isinstance(q['answer'], list)
        
        if self.current_mode == 'random':
            if self.random_submitted: return
            current_sel = self.random_choices.get(q_key, [])
        else:
            hist_source = self.wrong_history if self.current_mode == 'wrong' else self.progress['history']
            if q_key in hist_source: return
            current_sel = self.current_selected

        if is_multi:
            if idx in current_sel: current_sel.remove(idx)
            else: current_sel.append(idx)
        else:
            current_sel = [idx]
            
        if self.current_mode == 'random':
            self.random_choices[q_key] = current_sel
        else:
            self.current_selected = current_sel
            
        self.refresh_option_bar_colors()
        self.update_answer_sheet_colors()

    def refresh_option_bar_colors(self):
        q = self.current_list[self.current_idx]
        q_key = self.get_q_key(q)
        is_multi = isinstance(q['answer'], list)
        ans = q['answer']
        
        has_history = False
        hist_ans = None
        
        if self.current_mode == 'random':
            if self.random_submitted:
                has_history = True
                hist_ans = self.random_history.get(q_key, {}).get('user_ans', [])
            else:
                current_sel = self.random_choices.get(q_key, [])
        else:
            hist_source = self.wrong_history if self.current_mode == 'wrong' else self.progress['history']
            if q_key in hist_source:
                has_history = True
                hist_raw = hist_source[q_key].get('user_ans')
                hist_ans = hist_raw if isinstance(hist_raw, list) else [hist_raw]
            else:
                current_sel = self.current_selected

        for i, btn in enumerate(self.option_widgets):
            if has_history:
                btn.config(state=tk.DISABLED)
                is_correct_target = i in ans if is_multi else i == ans
                is_user_selected = i in hist_ans if hist_ans else False
                
                if is_correct_target:
                    btn.config(bg="#C8E6C9", fg="#2E7D32", disabledforeground="#2E7D32") 
                elif is_user_selected:
                    btn.config(bg="#FFCDD2", fg="#C62828", disabledforeground="#C62828") 
                else:
                    btn.config(bg="#F5F5F5", fg="#757575", disabledforeground="#757575")
            else:
                btn.config(state=tk.NORMAL)
                if i in current_sel:
                    btn.config(bg="#BBDEFB", fg="#0D47A1")
                else:
                    btn.config(bg="#F5F5F5", fg="#333333")

    # ==================== 判题与模拟交卷逻辑 ====================
    def handle_submit_action(self):
        if self.current_mode == 'random':
            self.submit_random_exam()
        else:
            self.submit_single_question()

    def submit_single_question(self):
        if self.has_answered: return
        if not self.current_selected:
            messagebox.showwarning("提示", "请先点击一个长条选项后再确定输入！")
            return
            
        q = self.current_list[self.current_idx]
        ans = q['answer']
        is_multi = isinstance(ans, list)
        q_key = self.get_q_key(q)
        
        if is_multi:
            user_ans = self.current_selected
            is_correct = (sorted(user_ans) == sorted(ans))
        else:
            user_ans = self.current_selected[0]
            is_correct = (user_ans == ans)
            
        self.has_answered = True
        status_str = "correct" if is_correct else "wrong"
        
        if self.current_mode == 'wrong':
            self.wrong_history[q_key] = {"status": status_str, "user_ans": user_ans}
            if is_correct: self.resolved_wrong_keys.add(q_key)
            else: self.resolved_wrong_keys.discard(q_key)
            self.progress['history'][q_key] = {"status": status_str, "user_ans": user_ans}
        else:
            self.progress['history'][q_key] = {"status": status_str, "user_ans": user_ans}
            if not is_correct:
                if not any(self.get_q_key(wq) == q_key for wq in self.wrong_questions):
                    self.wrong_questions.append(q)
                    
        self.save_state()
        self.load_question()

    def submit_random_exam(self):
        if self.random_submitted: return
        
        unanswered_count = 0
        for q in self.current_list:
            q_key = self.get_q_key(q)
            if q_key not in self.random_choices or not self.random_choices[q_key]:
                unanswered_count += 1
                
        if unanswered_count > 0:
            if not messagebox.askyesno("交卷确认", f"当前还剩 {unanswered_count} 题未做，确认提交吗？"):
                return
                
        score = 0
        exam_details = {}
        for q in self.current_list:
            q_key = self.get_q_key(q)
            user_sel = self.random_choices.get(q_key, [])
            ans = q['answer']
            is_multi = isinstance(ans, list)
            
            if is_multi:
                is_correct = (sorted(user_sel) == sorted(ans))
            else:
                is_correct = (len(user_sel) == 1 and user_sel[0] == ans)
                
            if is_correct:
                score += 5  
            else:
                if not any(self.get_q_key(wq) == q_key for wq in self.wrong_questions):
                    self.wrong_questions.append(q)
                    
            exam_details[q_key] = {
                "user_ans": user_sel,
                "status": "correct" if is_correct else "wrong"
            }
            
        self.random_submitted = True
        self.random_history = exam_details
        
        history_node = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": score,
            "details": exam_details
        }
        self.progress["random_records"].append(history_node)
        
        self.save_state()
        messagebox.showinfo("模拟考成绩单", f"交卷结算完毕！\n您的得分为：{score} 分 (满分 100 分)")
        self.load_question()

    def show_analysis(self, q, ans, is_correct):
        analysis_txt = q.get('analysis', '').strip()
        if not analysis_txt: analysis_txt = "无"
        if isinstance(ans, list): correct_str = "、".join([chr(65+i) for i in ans])
        else: correct_str = chr(65+ans)
        
        result_text = "🎉 回答正确！" if is_correct else "❌ 回答错误！"
        color = "#2E7D32" if is_correct else "#C62828"
        full_text = f"{result_text}\n\n【正确答案】 {correct_str}\n\n【解析说明】\n{analysis_txt}"
        self.lbl_analysis.config(text=full_text, fg=color)
        self.analysis_frame.pack(fill=tk.X, pady=(15, 5))

    def show_random_history_window(self):
        win = tk.Toplevel(self.root)
        bank_name = os.path.splitext(self.q_file)[0]
        win.title(f"用户 [{self.current_user}] - 题库 [{bank_name}] 的模拟考历史")
        win.geometry("520x420")
        win.grab_set() 
        
        txt = tk.Text(win, font=("Microsoft YaHei", 10), wrap=tk.WORD, padx=12, pady=12, bg="#F9F9F9")
        sc = ttk.Scrollbar(win, command=txt.yview)
        txt.configure(yscrollcommand=sc.set)
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        records = self.progress.get("random_records", [])
        if not records:
            txt.insert(tk.END, "💡 当前账号在此题库下暂无任何模拟考试记录。")
        else:
            txt.insert(tk.END, f"=== 📊 共计查找到 {len(records)} 次考试日志 ===\n\n")
            for idx, r in enumerate(reversed(records)):
                txt.insert(tk.END, f"⏱ 考试时间: {r['time']}\n")
                txt.insert(tk.END, f"💯 模拟得分: {r['score']} 分 (满分100分)\n")
                txt.insert(tk.END, f"{'-'*45}\n")
        txt.config(state=tk.DISABLED)

    # ==================== 导航与模式切换 ====================
    def switch_bank(self):
        """新增：在答题页面切换回题库选择页面"""
        if messagebox.askyesno("切换确认", "确认要保存当前进度并切换到其他题库吗？"):
            self.save_state()
            # 销毁现有主界面的所有小部件
            for w in self.root.winfo_children(): w.destroy()
            # 重新回到题库选择页面
            self.show_bank_selection_page()

    def next_q(self):
        if self.current_idx < len(self.current_list) - 1:
            self.current_idx += 1
        else:
            messagebox.showinfo("提示", "已经是本列表最后一题了！")
            return
        if self.current_mode == 'seq':
            self.progress['seq_idx'] = self.current_idx
            self.save_state()
        self.load_question()

    def prev_q(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            if self.current_mode == 'seq':
                self.progress['seq_idx'] = self.current_idx
                self.save_state()
            self.load_question()
        else:
            messagebox.showinfo("提示", "当前已经是第一题了！")

    def change_mode(self, mode):
        if self.resolved_wrong_keys:
            self.wrong_questions = [q for q in self.wrong_questions if self.get_q_key(q) not in self.resolved_wrong_keys]
            self.resolved_wrong_keys.clear()
            self.progress["resolved_wrong_keys"] = []
            self.save_state()

        if mode == 'wrong' and not self.wrong_questions:
            messagebox.showinfo("提示", "当前题库的错题本空空如也，保持得真棒！")
            return
            
        self.current_mode = mode
        if mode == 'seq':
            self.current_list = self.all_questions
            self.current_idx = self.progress.get('seq_idx', 0)
        elif mode == 'random':
            self.current_list = random.sample(self.all_questions, min(20, len(self.all_questions)))
            self.current_idx = 0
            self.random_choices = {}
            self.random_history = {}
            self.random_submitted = False
        elif mode == 'wrong':
            self.current_list = self.wrong_questions
            self.current_idx = 0
            self.wrong_history = {}
            
        self.init_answer_sheet() 
        self.load_question()

    def update_stats_ui(self):
        total = len(self.all_questions)
        ans_count = len(self.progress['history']) 
        correct = sum(1 for v in self.progress['history'].values() if v.get('status') == "correct")
        acc = (correct / ans_count * 100) if ans_count > 0 else 0
        wrong_count = len(self.wrong_questions)
        
        bank_name = os.path.splitext(self.q_file)[0]
        mode_dict = {"seq": "顺序刷题", "random": "模拟考试(20题)", "wrong": "错题复习"}
        stat_text = (f"👤 账号: {self.current_user} | 📚 题库: [{bank_name}] | 模式: [{mode_dict[self.current_mode]}]\n"
                     f"去重总进度: {ans_count}/{total}   "
                     f"总正确率: {acc:.1f}%   "
                     f"错题本: {wrong_count}题")
        self.lbl_stats.config(text=stat_text)

    def on_closing(self):
        if hasattr(self, 'current_user') and self.q_file:
            self.save_state()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing) # 修复关闭窗口事件拦截
    root.eval('tk::PlaceWindow . center') 
    root.mainloop()