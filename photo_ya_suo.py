import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from datetime import datetime

IMG_SUFFIX = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]

class ImageCompressTool:
    def __init__(self, root):
        self.root = root
        self.root.title("图片批量压缩工具")
        self.root.geometry("650x550")
        self.stop_flag = False
        self.resize_mode = tk.StringVar(value="auto")

        self.src_path = tk.StringVar()
        self.out_path = tk.StringVar()
        self.w = tk.StringVar(value="1024")
        self.h = tk.StringVar(value="768")
        self.scale = tk.StringVar(value="85")

        tk.Label(root, text="源图片文件夹：").place(x=20, y=20)
        self.src_entry = tk.Entry(root, textvariable=self.src_path, width=60)
        self.src_entry.place(x=20, y=50)
        tk.Button(root, text="选择", command=self.select_src).place(x=490, y=48)

        tk.Label(root, text="处理模式：").place(x=20, y=90)

        self.auto_frame = tk.Frame(root)
        self.auto_frame.place(x=20, y=120)
        self.auto_radio = tk.Radiobutton(self.auto_frame, text="自动识别原图尺寸", variable=self.resize_mode, value="auto", command=self.update_resolution_ui)
        self.auto_radio.grid(row=0, column=0)
        self.auto_label = tk.Label(self.auto_frame, text="缩放比例：")
        self.auto_label.grid(row=0, column=1)
        self.scale_combo = ttk.Combobox(self.auto_frame, textvariable=self.scale, width=10, state="readonly")
        self.scale_combo['values'] = ["50", "55", "60", "65", "70", "75", "80", "85", "90"]
        self.scale_combo.grid(row=0, column=2)
        self.auto_pct = tk.Label(self.auto_frame, text="%")
        self.auto_pct.grid(row=0, column=3)

        self.fixed_frame = tk.Frame(root)
        self.fixed_frame.place(x=20, y=150)
        self.fixed_radio = tk.Radiobutton(self.fixed_frame, text="固定分辨率", variable=self.resize_mode, value="fixed", command=self.update_resolution_ui)
        self.fixed_radio.grid(row=0, column=0)
        self.fixed_w_label = tk.Label(self.fixed_frame, text="宽：")
        self.fixed_w_label.grid(row=0, column=1)
        self.w_entry = tk.Entry(self.fixed_frame, textvariable=self.w, width=10)
        self.w_entry.grid(row=0, column=2)
        self.fixed_x = tk.Label(self.fixed_frame, text="x")
        self.fixed_x.grid(row=0, column=3)
        self.fixed_h_label = tk.Label(self.fixed_frame, text="高：")
        self.fixed_h_label.grid(row=0, column=4)
        self.h_entry = tk.Entry(self.fixed_frame, textvariable=self.h, width=10)
        self.h_entry.grid(row=0, column=5)

        self.update_resolution_ui()

        tk.Label(root, text="输出目录（必须为空）：").place(x=20, y=190)
        self.out_entry = tk.Entry(root, textvariable=self.out_path, width=60)
        self.out_entry.place(x=20, y=220)
        tk.Button(root, text="选择", command=self.select_out).place(x=490, y=218)

        self.start_btn = tk.Button(root, text="开始压缩", command=self.on_start, font=("微软雅黑",12), width=15)
        self.start_btn.place(x=150, y=270)

        self.stop_btn = tk.Button(root, text="停止", command=self.on_stop, bg="#DC143C", fg="white", font=("微软雅黑",12), width=10, state=tk.DISABLED)
        self.stop_btn.place(x=350, y=270)

        self.status_label = tk.Label(root, text="等待操作...", fg="blue")
        self.status_label.place(x=20, y=330)

        self.current_label = tk.Label(root, text="", fg="green", wraplength=600)
        self.current_label.place(x=20, y=360)

        tk.Label(root, text="调试日志：").place(x=20, y=390)
        self.log_text = tk.Text(root, width=75, height=6, font=("Consolas", 9))
        self.log_text.place(x=20, y=415)
        self.log_text.insert(tk.END, "=== 日志开始 ===\n")
        self.log_text.config(state=tk.DISABLED)

    def update_resolution_ui(self):
        mode = self.resize_mode.get()
        if mode == "fixed":
            self.auto_radio.config(state=tk.NORMAL)
            self.auto_label.config(fg="gray")
            self.scale_combo.config(state=tk.DISABLED)
            self.auto_pct.config(fg="gray")
            
            self.fixed_radio.config(state=tk.NORMAL)
            self.fixed_w_label.config(fg="black")
            self.w_entry.config(state=tk.NORMAL)
            self.fixed_x.config(fg="black")
            self.fixed_h_label.config(fg="black")
            self.h_entry.config(state=tk.NORMAL)
        else:
            self.auto_radio.config(state=tk.NORMAL)
            self.auto_label.config(fg="black")
            self.scale_combo.config(state="readonly")
            self.auto_pct.config(fg="black")
            
            self.fixed_radio.config(state=tk.NORMAL)
            self.fixed_w_label.config(fg="gray")
            self.w_entry.config(state=tk.DISABLED)
            self.fixed_x.config(fg="gray")
            self.fixed_h_label.config(fg="gray")
            self.h_entry.config(state=tk.DISABLED)
        self.update_output_dir()

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
        print(msg)

    def update_output_dir(self):
        src_dir = self.src_path.get().strip()
        if not src_dir or not os.path.isdir(src_dir):
            self.out_path.set("")
            return
        
        src_name = os.path.basename(src_dir)
        
        if self.resize_mode.get() == "fixed":
            w, h = int(self.w.get()) if self.w.get().isdigit() else 1024, int(self.h.get()) if self.h.get().isdigit() else 768
            out_dir = f"{src_name}_{w}x{h}"
        else:
            scale = self.scale.get()
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_dir = f"{src_name}_scaled_{scale}p_{now}"
        
        default_out = os.path.join(os.path.dirname(src_dir), out_dir)
        self.out_path.set(default_out)

    def select_src(self):
        self.log("点击选择源文件夹按钮")
        path = filedialog.askdirectory(title="选择图片文件夹")
        if path:
            self.log(f"选择源文件夹: {path}")
            self.src_path.set(path)
            self.update_output_dir()

    def select_out(self):
        self.log("点击选择输出目录按钮")
        path = filedialog.askdirectory(title="选择输出目录（必须为空）")
        if path:
            self.log(f"选择输出目录: {path}")
            if os.listdir(path):
                self.log("警告: 输出目录不为空")
                messagebox.showwarning("警告", "输出目录必须为空！")
                return
            self.out_path.set(path)

    def on_stop(self):
        self.log("点击停止按钮")
        self.stop_flag = True
        self.status_label.config(text="正在停止...")

    def on_start(self):
        self.log("=== 点击开始压缩按钮 ===")
        
        src_dir = self.src_path.get().strip()
        self.log(f"源目录: '{src_dir}'")
        
        if not os.path.isdir(src_dir):
            self.log("错误: 源文件夹不存在")
            messagebox.showerror("错误", "请先选择合法的源文件夹")
            return
        self.log("源文件夹存在")

        out_path = self.out_path.get().strip()
        self.log(f"输出目录: '{out_path}'")
        
        if not out_path:
            self.log("错误: 输出目录为空")
            messagebox.showerror("错误", "请选择输出目录")
            return
        
        if os.path.exists(out_path) and os.listdir(out_path):
            self.log("错误: 输出目录不为空")
            messagebox.showerror("错误", "输出目录必须为空！")
            return
        
        try:
            os.makedirs(out_path, exist_ok=True)
            self.log("输出目录创建成功")
        except PermissionError:
            self.log("错误: 无法创建输出目录")
            messagebox.showerror("权限错误", f"无法创建输出目录：{out_path}\n\n请选择其他文件夹或使用管理员权限运行")
            return

        resize_mode = self.resize_mode.get()
        self.log(f"处理模式: {resize_mode}")
        
        if resize_mode == "fixed":
            try:
                w, h = int(self.w.get()), int(self.h.get())
                self.log(f"分辨率: {w}x{h}")
            except Exception as e:
                self.log(f"错误: 分辨率无效 - {e}")
                messagebox.showerror("错误", "分辨率必须是数字")
                return
        else:
            scale = int(self.scale.get())
            self.log(f"缩放比例: {scale}%")

        self.stop_flag = False
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        total = 0
        self.log("开始统计图片数量...")
        for root, _, files in os.walk(src_dir):
            if self.stop_flag:
                self.log("检测到停止信号")
                break
            for f in files:
                if os.path.splitext(f)[1].lower() in IMG_SUFFIX:
                    total += 1
            self.root.update()
        
        if self.stop_flag:
            self.log("统计阶段被停止")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.current_label.config(text="")
            self.status_label.config(text="已停止！")
            messagebox.showinfo("已停止", "统计阶段已停止")
            return
        
        self.log(f"发现 {total} 张图片")

        processed = 0
        self.status_label.config(text=f"发现 {total} 张图片，开始压缩...")
        self.root.update()

        self.log("开始压缩...")
        for root_path, _, files in os.walk(src_dir):
            if self.stop_flag:
                self.log("检测到停止信号")
                break

            rel_path = os.path.relpath(root_path, src_dir)
            if rel_path == '.':
                out_sub = out_path
            else:
                out_sub = os.path.join(out_path, rel_path)
            os.makedirs(out_sub, exist_ok=True)

            for name in files:
                if self.stop_flag:
                    self.log("检测到停止信号")
                    break

                ext = os.path.splitext(name)[1].lower()
                if ext not in IMG_SUFFIX:
                    continue

                img_path = os.path.join(root_path, name)
                pure_name = os.path.splitext(name)[0]
                
                if resize_mode == "fixed":
                    new_name = f"{pure_name}_{w}x{h}{ext}"
                else:
                    new_name = f"{pure_name}_scaled{ext}"
                
                save_path = os.path.join(out_sub, new_name)

                self.current_label.config(text=f"处理: {rel_path}/{name}")
                self.log(f"处理: {name}")
                self.root.update()

                try:
                    img = Image.open(img_path)
                    if resize_mode == "fixed":
                        img = img.resize((w, h), Image.Resampling.LANCZOS)
                    else:
                        width, height = img.size
                        new_width = int(width * scale / 100)
                        new_height = int(height * scale / 100)
                        self.log(f"原图尺寸: {width}x{height} -> {new_width}x{new_height}")
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    img.save(save_path, quality=85)
                    processed += 1
                    self.status_label.config(text=f"已处理: {processed}/{total}")
                    self.log(f"成功: {new_name}")
                except Exception as e:
                    self.log(f"失败: {name} - {e}")

                self.root.update()

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.current_label.config(text="")

        if self.stop_flag:
            self.log(f"已停止！处理了 {processed} 张图片")
            self.status_label.config(text=f"已停止！处理了 {processed} 张")
            messagebox.showinfo("已停止", f"已处理 {processed} 张图片")
        else:
            self.log(f"完成！处理了 {processed} 张图片")
            self.status_label.config(text=f"完成！保存至: {out_path}")
            messagebox.showinfo("完成", f"全部完成！\n输出目录: {out_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCompressTool(root)
    root.mainloop()