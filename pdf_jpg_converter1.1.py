import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from pdf2image import convert_from_path

Image.MAX_IMAGE_PIXELS = None  # 解除像素限制（Pillow防止大图报错）

def get_poppler_path():
    possible = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poppler", "bin")
    if os.path.exists(possible):
        return possible
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        possible = os.path.join(base_path, "poppler", "bin")
        if os.path.exists(possible):
            return possible
    return None

POPPLER_PATH = get_poppler_path()

def pdf_to_jpg(pdf_path, dpi=300):
    """
    优化版：一页一页转换，极低内存占用，适合上千页大PDF。
    依赖 PyPDF2 统计总页数。
    """
    try:
        from PyPDF2 import PdfReader
        if not POPPLER_PATH:
            raise RuntimeError("未找到poppler，请确认poppler目录与脚本同级，并包含bin文件夹")
        pdf_dir = os.path.dirname(pdf_path)
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        out_dir = os.path.join(pdf_dir, pdf_name)
        os.makedirs(out_dir, exist_ok=True)
        # 获取总页数
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        out_files = []
        for page_number in range(1, num_pages + 1):
            pages = convert_from_path(
                pdf_path, dpi, poppler_path=POPPLER_PATH,
                first_page=page_number, last_page=page_number
            )
            page = pages[0]
            fname = f"{pdf_name}_page{page_number}.jpg"
            out_path = os.path.join(out_dir, fname)
            page.save(out_path, "JPEG")
            out_files.append(out_path)
            del page
        return True, out_files, out_dir
    except Exception as e:
        return False, str(e), None

def jpg_to_pdf(jpg_paths):
    try:
        if not jpg_paths:
            return False, "未选择JPG文件", None
        images = []
        for p in jpg_paths:
            img = Image.open(p)
            # 保证所有图片为RGB（有些JPG可能是灰度或带透明通道）
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            images.append(img)
        if not images:
            return False, "No images selected.", None
        out_dir = os.path.dirname(jpg_paths[0])
        out_file = os.path.join(out_dir, "合并输出.pdf")
        images[0].save(out_file, save_all=True, append_images=images[1:])
        return True, out_file, out_dir
    except Exception as e:
        return False, str(e), None

class PDFJPGConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF <-> JPG Converter")
        self.root.geometry("650x400")
        self.create_widgets()

    def create_widgets(self):
        self.tab_control = ttk.Notebook(self.root)
        self.tab_pdf2jpg = ttk.Frame(self.tab_control)
        self.tab_jpg2pdf = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_pdf2jpg, text="PDF转JPG")
        self.tab_control.add(self.tab_jpg2pdf, text="JPG转PDF")
        self.tab_control.pack(expand=1, fill="both")

        # PDF2JPG
        self.pdf_files = []
        self.dpi = tk.IntVar(value=300)
        ttk.Label(self.tab_pdf2jpg, text="选择PDF文件（支持多选）:").pack(anchor="w", padx=10, pady=5)
        self.btn_select_pdf = ttk.Button(self.tab_pdf2jpg, text="选择PDF", command=self.select_pdf_files)
        self.btn_select_pdf.pack(anchor="w", padx=20)
        self.pdf_listbox = tk.Listbox(self.tab_pdf2jpg, height=4)
        self.pdf_listbox.pack(fill="x", padx=20, pady=5)
        ttk.Label(self.tab_pdf2jpg, text="DPI（分辨率，默认300）:").pack(anchor="w", padx=10, pady=5)
        self.entry_dpi = ttk.Entry(self.tab_pdf2jpg, textvariable=self.dpi, width=10)
        self.entry_dpi.pack(anchor="w", padx=20, pady=5)
        self.btn_convert_pdf2jpg = ttk.Button(self.tab_pdf2jpg, text="开始转换", command=self.run_pdf2jpg)
        self.btn_convert_pdf2jpg.pack(pady=5)
        self.progress_pdf2jpg = ttk.Progressbar(self.tab_pdf2jpg, orient="horizontal", mode="indeterminate", length=300)
        self.progress_pdf2jpg.pack(pady=5)

        # JPG2PDF
        self.jpg_files = []
        frame_jpg = ttk.Frame(self.tab_jpg2pdf)
        frame_jpg.pack(fill="x", padx=20, pady=5)
        ttk.Label(frame_jpg, text="选择JPG文件（可多选，支持排序，按顺序合成PDF）:").grid(row=0, column=0, sticky="w", columnspan=3)
        self.btn_select_jpg = ttk.Button(frame_jpg, text="选择JPG", command=self.select_jpg_files)
        self.btn_select_jpg.grid(row=1, column=0, sticky="w", pady=2)
        self.btn_up = ttk.Button(frame_jpg, text="上移", command=self.move_up)
        self.btn_up.grid(row=1, column=1, padx=4, pady=2)
        self.btn_down = ttk.Button(frame_jpg, text="下移", command=self.move_down)
        self.btn_down.grid(row=1, column=2, pady=2)

        self.jpg_listbox = tk.Listbox(self.tab_jpg2pdf, height=8, selectmode=tk.SINGLE)
        self.jpg_listbox.pack(fill="x", padx=20, pady=5)
        self.btn_convert_jpg2pdf = ttk.Button(self.tab_jpg2pdf, text="开始转换", command=self.run_jpg2pdf)
        self.btn_convert_jpg2pdf.pack(pady=5)
        self.progress_jpg2pdf = ttk.Progressbar(self.tab_jpg2pdf, orient="horizontal", mode="indeterminate", length=300)
        self.progress_jpg2pdf.pack(pady=5)

        # 版权信息标签
        self.copyright_label = ttk.Label(self.root, text="灯火通明（济宁）网络有限公司", anchor='e')
        self.copyright_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-5)

    # PDF2JPG
    def select_pdf_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if files:
            self.pdf_files = files
            self.pdf_listbox.delete(0, tk.END)
            for f in files:
                self.pdf_listbox.insert(tk.END, os.path.basename(f))

    def run_pdf2jpg(self):
        if not self.pdf_files:
            messagebox.showwarning("提示", "请先选择PDF文件")
            return
        try:
            dpi_val = int(self.dpi.get())
        except ValueError:
            messagebox.showwarning("提示", "DPI应为整数")
            return
        self.progress_pdf2jpg.start(10)
        threading.Thread(target=self.do_pdf2jpg, args=(dpi_val,), daemon=True).start()

    def do_pdf2jpg(self, dpi_val):
        for idx, pdf in enumerate(self.pdf_files):
            ok, result, out_dir = pdf_to_jpg(pdf, dpi=dpi_val)
            if not ok:
                self.progress_pdf2jpg.stop()
                messagebox.showerror("转换失败", f"{os.path.basename(pdf)} 转换失败: {result}")
                return
        self.progress_pdf2jpg.stop()
        messagebox.showinfo("完成", f"PDF转换完成！图片已保存到原文件夹下的新文件夹。")

    # JPG2PDF
    def select_jpg_files(self):
        files = filedialog.askopenfilenames(filetypes=[("JPEG/JPG Files", "*.jpg;*.jpeg")])
        if files:
            self.jpg_files = list(files)
            self.refresh_jpg_listbox()

    def refresh_jpg_listbox(self):
        self.jpg_listbox.delete(0, tk.END)
        for f in self.jpg_files:
            self.jpg_listbox.insert(tk.END, os.path.basename(f))

    def move_up(self):
        sel = self.jpg_listbox.curselection()
        if not sel or sel[0] == 0:
            return
        idx = sel[0]
        self.jpg_files[idx-1], self.jpg_files[idx] = self.jpg_files[idx], self.jpg_files[idx-1]
        self.refresh_jpg_listbox()
        self.jpg_listbox.selection_set(idx-1)

    def move_down(self):
        sel = self.jpg_listbox.curselection()
        if not sel or sel[0] == len(self.jpg_files)-1:
            return
        idx = sel[0]
        self.jpg_files[idx+1], self.jpg_files[idx] = self.jpg_files[idx], self.jpg_files[idx+1]
        self.refresh_jpg_listbox()
        self.jpg_listbox.selection_set(idx+1)

    def run_jpg2pdf(self):
        if not self.jpg_files:
            messagebox.showwarning("提示", "请先选择JPG文件")
            return
        self.progress_jpg2pdf.start(10)
        threading.Thread(target=self.do_jpg2pdf, daemon=True).start()

    def do_jpg2pdf(self):
        ok, out_file, out_dir = jpg_to_pdf(self.jpg_files)
        self.progress_jpg2pdf.stop()
        if ok:
            messagebox.showinfo("完成", f"PDF已生成：{out_file}")
        else:
            messagebox.showerror("转换失败", f"错误信息: {out_file}")

def main():
    root = tk.Tk()
    app = PDFJPGConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()