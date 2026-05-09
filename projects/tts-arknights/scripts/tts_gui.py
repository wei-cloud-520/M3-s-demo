"""
凯尔希 TTS 桌面版 v2 - 纯requests，无需gradio_client
依赖: pip install requests websocket-client
"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import subprocess
import os
import sys
import threading
import json
import requests
from datetime import datetime

# ============ 配置 ============
API_URL = "http://127.0.0.1:9872"
REF_AUDIO = "/data/kaltsit_zh/char_003_kalts_boc#6_CN_001.wav"
DOCKER_DIR = r"E:\sound model\GPT-SoVITS-Train"
FN_INDEX = 3
# ================================


def get_container_id():
    try:
        result = subprocess.run(
            'docker ps --filter ancestor=breakstring/gpt-sovits --format {{.ID}}',
            shell=True, capture_output=True, text=True
        )
        lines = [l for l in result.stdout.strip().split("\n") if l]
        return lines[0] if lines else None
    except:
        return None


def gradio_predict(data, fn_index, api_url):
    """通过HTTP调用Gradio API"""
    session = requests.Session()

    # 获取API信息
    resp = session.get(f"{api_url}/info")
    if resp.status_code != 200:
        raise Exception(f"无法连接到 {api_url}")

    # 发起predict
    resp = session.post(
        f"{api_url}/api/predict",
        json={"data": data, "fn_index": fn_index},
        timeout=120
    )
    if resp.status_code == 200:
        result = resp.json()
        return result.get("data", [None])[0]
    else:
        raise Exception(f"API返回错误: {resp.status_code} {resp.text[:200]}")


class TTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("凯尔希 TTS")
        self.root.geometry("600x520")
        self.root.configure(bg="#1a1a2e")

        self.container_id = get_container_id()
        self.last_output = None

        # 标题
        tk.Label(root, text="🦎 凯尔希 TTS", font=("微软雅黑", 16, "bold"),
                fg="#e0e0e0", bg="#1a1a2e").pack(pady=10)

        # 容器状态
        if self.container_id:
            st = f"容器已连接: {self.container_id[:12]}"
            sc = "#4ecca3"
        else:
            st = "⚠ 容器未运行"
            sc = "#ff6b6b"
        self.status_label = tk.Label(root, text=st, font=("微软雅黑", 9),
                                     fg=sc, bg="#1a1a2e")
        self.status_label.pack()

        # 文本输入
        tk.Label(root, text="输入文本:", fg="#e0e0e0", bg="#1a1a2e",
                font=("微软雅黑", 10)).pack(anchor="w", padx=20, pady=(10, 2))

        self.text_input = scrolledtext.ScrolledText(
            root, height=10, width=65, font=("微软雅黑", 11),
            bg="#16213e", fg="#e0e0e0", insertbackground="#e0e0e0",
            wrap=tk.WORD, relief=tk.FLAT
        )
        self.text_input.pack(padx=20)

        # 切分模式
        mf = tk.Frame(root, bg="#1a1a2e")
        mf.pack(pady=5)
        tk.Label(mf, text="切分:", fg="#e0e0e0", bg="#1a1a2e",
                font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=5)
        self.slice_var = tk.StringVar(value="自动")
        for m in ["自动", "不切分", "凑四句一切", "凑50字一切"]:
            tk.Radiobutton(mf, text=m, variable=self.slice_var, value=m,
                          fg="#e0e0e0", bg="#1a1a2e", selectcolor="#16213e",
                          font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=3)

        # 按钮
        bf = tk.Frame(root, bg="#1a1a2e")
        bf.pack(pady=10)

        self.synth_btn = tk.Button(
            bf, text="合成语音", font=("微软雅黑", 11, "bold"),
            bg="#4ecca3", fg="#1a1a2e", relief=tk.FLAT,
            width=12, command=self.synthesize
        )
        self.synth_btn.pack(side=tk.LEFT, padx=5)

        self.play_btn = tk.Button(
            bf, text="播放", font=("微软雅黑", 11),
            bg="#0f3460", fg="#e0e0e0", relief=tk.FLAT,
            width=8, command=self.play_audio, state=tk.DISABLED
        )
        self.play_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = tk.Button(
            bf, text="另存为", font=("微软雅黑", 11),
            bg="#0f3460", fg="#e0e0e0", relief=tk.FLAT,
            width=8, command=self.save_audio, state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.progress_label = tk.Label(root, text="", font=("微软雅黑", 9),
                                       fg="#4ecca3", bg="#1a1a2e")
        self.progress_label.pack()

    def synthesize(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("提示", "请输入文本")
            return

        if not self.container_id:
            self.container_id = get_container_id()
        if not self.container_id:
            messagebox.showerror("错误", "Docker容器未运行")
            return

        slice = self.slice_var.get()
        if slice == "自动":
            slice = "凑四句一切" if len(text) > 100 else "不切分"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"/data/output_{timestamp}.wav"

        self.synth_btn.config(state=tk.DISABLED, text="合成中...")
        self.progress_label.config(text="正在合成，请稍候...")
        self.root.update()

        def worker():
            try:
                result = gradio_predict(
                    data=[REF_AUDIO, "", "Chinese", text, "Chinese", slice, 20, 0.6, 0.3, True],
                    fn_index=FN_INDEX,
                    api_url=API_URL
                )
                if result:
                    # result是容器内路径
                    import shutil
                    shutil.copy2(result, output_file)
                    self.root.after(0, lambda: self._on_success(output_file))
                else:
                    self.root.after(0, lambda: self._on_error("返回为空"))
            except Exception as e:
                self.root.after(0, lambda: self._on_error(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_success(self, path):
        self.last_output = path
        self.synth_btn.config(state=tk.NORMAL, text="合成语音")
        self.progress_label.config(text="✓ 合成完成")
        self.play_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
        self.play_audio()

    def _on_error(self, msg):
        self.synth_btn.config(state=tk.NORMAL, text="合成语音")
        self.progress_label.config(text=f"✗ {msg}")
        messagebox.showerror("错误", msg[:300])

    def play_audio(self):
        if not self.last_output:
            return
        win_path = self.last_output.replace("/data/", DOCKER_DIR + "\\").replace("/", "\\")
        if os.path.exists(win_path):
            os.system(f'start "" "{win_path}"')

    def save_audio(self):
        if not self.last_output or not self.container_id:
            return
        save_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV", "*.wav")],
            initialfile=f"kaltsit_{datetime.now().strftime('%H%M%S')}.wav"
        )
        if save_path:
            try:
                subprocess.run(
                    f'docker cp {self.container_id}:{self.last_output} "{save_path}"',
                    shell=True, check=True
                )
                messagebox.showinfo("成功", f"已保存: {save_path}")
            except Exception as e:
                messagebox.showerror("错误", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()
