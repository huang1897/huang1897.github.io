import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import pyperclip
import threading
import time
import sqlite3
import urllib.request
import bcrypt
import sys
import vlc
import datetime
import sys
import requests
import os
import psutil
from tkinter import messagebox
import urllib3
import warnings
import requests
from tkinter import messagebox
from datetime import datetime
import warnings

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
def check_for_updates():
    """检查更新并下载新版本"""
    update_url = "https://gitee.com/cclchuang/huang1897.github.io/raw/main/xzdz.txt"  # 替换为您的TXT文件URL

    try:
        response = requests.get(update_url)
        response.raise_for_status()
        
        lines = response.text.strip().splitlines()  # 获取所有行
        if not lines or len(lines) == 0:
            messagebox.showerror("更新失败", "更新文件为空，无法获取新版本链接。")
            return

        new_version_url = lines[0]  # 获取URL的第一行作为新版本链接
        print(f"New version URL: {new_version_url}")  # 打印出新的版本 URL
        
        if not new_version_url.startswith("http://") and not new_version_url.startswith("https://"):
            messagebox.showerror("更新失败", "新版本链接格式不正确。")
            return
            
        download_new_version(new_version_url)

    except requests.RequestException as e:
        messagebox.showerror("更新失败", f"无法检查更新: {e}")


def download_new_version(url):
    """下载新版本并替换当前程序"""
    local_filename = os.path.join(os.path.dirname(sys.argv[0]), 'KTV视频下载工具2.0.exe')  # 当前程序的路径

    try:
        response = requests.get(url, stream=True)  # 逐块下载
        response.raise_for_status()

        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        messagebox.showinfo("更新成功", "软件更新完成，请重新启动程序。")
        sys.exit()  # 退出当前程序，以便用户可以重新启动更新后的版本

    except requests.RequestException as e:
        messagebox.showerror("下载失败", f"无法下载新版本: {e}")

def save_login_info(username, password):
    with open(os.path.join('data', 'login_info.json'), 'w') as f:  # 修改为指向 data 目录下的文件
        json.dump({'username': username, 'password': password}, f)

def load_login_info():
    try:
        with open(os.path.join('data', 'login_info.json'), 'r') as f:  # 修改为指向 data 目录下的文件
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

class VideoPlayer:
    current_instance = None  # 类变量，用于存储当前实例
    last_audio_track_index = 0  # 默认音轨索引

    def __init__(self, master):
        self.master = master
        self.master.title("KTV点歌器")


        if VideoPlayer.current_instance is not None:
            return

        VideoPlayer.current_instance = self  # 创建当前实例

        # 创建VLC实例
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()

        # 初始化已点歌曲列表和当前歌曲索引
        self.played_song_list = []  # 以列表形式存储已点歌曲
        self.current_song_index = -1  # 当前播放歌曲的索引
        self.is_playing = False  # 播放状态标识
        self.current_audio_track_index = 0  # 默认音轨索引
        self.is_seeking = False  # 新增：标记是否正在拖动进度条

        # 创建用于显示视频的Canvas
        self.video_frame = tk.Frame(self.master, bg="black")
        self.video_frame.grid(row=0, column=0, columnspan=8, sticky="nsew")

        self.canvas = tk.Canvas(self.video_frame, bg="black", width=800, height=450)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        

        # 控制按钮
        self.controls_frame = tk.Frame(self.master)  # 修改为实例变量
        self.controls_frame.grid(row=1, column=0, columnspan=8, pady=10, sticky="nsew")
        
        # 创建重播按钮
        self.replay_button = tk.Button(self.controls_frame, text="重播", command=self.replay_video, width=10)
        self.replay_button.grid(row=0, column=0, padx=5, sticky="nsew")

        # 创建暂停按钮
        self.pause_button = tk.Button(self.controls_frame, text="暂停", command=self.pause_video, width=10)
        self.pause_button.grid(row=0, column=1, padx=5, sticky="nsew")

        # 创建停止按钮
        self.stop_button = tk.Button(self.controls_frame, text="停止", command=self.stop_video, width=10)
        self.stop_button.grid(row=0, column=2, padx=5, sticky="nsew")

        # 创建切歌按钮
        self.next_button = tk.Button(self.controls_frame, text="切歌", command=self.play_next_song, width=10)
        self.next_button.grid(row=0, column=3, padx=5, sticky="nsew")


        # 创建原唱按钮
        self.original_button = tk.Button(self.controls_frame, text="原唱", command=lambda: self.set_audio_track(1), width=10)
        self.original_button.grid(row=0, column=4, padx=5, sticky="nsew")

        # 创建伴唱按钮
        self.伴唱_button = tk.Button(self.controls_frame, text="伴唱", command=lambda: self.set_audio_track(2), width=10)
        self.伴唱_button.grid(row=0, column=5, padx=5, sticky="nsew")

        # 创建全屏按钮
        self.fullscreen_button = tk.Button(self.controls_frame, text="全屏", command=self.toggle_fullscreen, width=10)
        self.fullscreen_button.grid(row=0, column=6, padx=5, sticky="nsew")

        # 创建添加本地视频的按钮
        self.add_local_video_button = tk.Button(self.controls_frame, text="添加视频", command=self.add_local_video, width=10)
        self.add_local_video_button.grid(row=0, column=7, padx=5, sticky="nsew")  # 在第0行第7列放置
        # 在控制按钮区添加“添加目录”按钮
        self.add_directory_button = tk.Button(self.controls_frame, text="添加目录", command=self.add_directory, width=10)
        self.add_directory_button.grid(row=0, column=8, padx=5, sticky="nsew")  # 在第0行第8列放置
        # 音量控制
        self.volume_scale = tk.Scale(self.master, from_=0, to=100, orient=tk.HORIZONTAL, label="音量", length=200)
        self.volume_scale.set(90)  # 默认音量为90%
        self.volume_scale.grid(row=3, column=4, columnspan=4, pady=5, padx=(5, 10), sticky="nsew")  # 放置在第3行第0列，跨越3列
        self.volume_scale.bind("<ButtonRelease-1>", self.set_volume)
        # 进度条
        self.progress_scale = tk.Scale(self.master, from_=0, to=100, orient=tk.HORIZONTAL, label="进度", length=200)
        self.progress_scale.grid(row=3, column=0, columnspan=4, pady=5, padx=(10, 5), sticky="nsew")  # 放置在第3行第3列，跨越3列
        self.progress_scale.bind("<ButtonPress-1>", self.start_seek)  # 按下事件
        self.progress_scale.bind("<ButtonRelease-1>", self.seek_video)  # 释放事件
        self.ff_button = tk.Button(self.controls_frame, text="快进", command=self.fast_forward, width=10)
        self.rew_button = tk.Button(self.controls_frame, text="快退", command=self.rewind, width=10)
 



        # 已点歌曲列表
        self.played_song_list_frame = tk.Frame(self.master)
        self.played_song_list_frame.grid(row=4, column=0, columnspan=8, pady=10, sticky="nsew")  # 添加sticky属性使其适应

        self.played_song_listbox = tk.Listbox(self.played_song_list_frame, height=10, width=50, selectmode=tk.MULTIPLE)  
        self.played_song_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)  # 添加padx参数使左右距离窗口20个像素


        # 创建滚动条
        self.played_scrollbar = tk.Scrollbar(self.played_song_list_frame)
        self.played_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.played_song_listbox.config(yscrollcommand=self.played_scrollbar.set)
        self.played_scrollbar.config(command=self.played_song_listbox.yview)

        # 绑定已点歌曲列表的双击事件
        self.played_song_listbox.bind("<Double-Button-1>", self.play_played_song)
        self.master.bind("<Down>", self.play_next_song) 
        

        # 创建右键菜单
        self.popup_menu = tk.Menu(self.master, tearoff=0)
        self.popup_menu.add_command(label="删除", command=self.delete_selected_songs)
        self.popup_menu.add_command(label="清空列表", command=self.clear_played_song_list)

        # 绑定右键菜单
        self.played_song_listbox.bind("<Button-3>", self.show_popup_menu)

        # 绑定回车键来切换全屏
        self.master.bind("<Return>", self.toggle_fullscreen)
        self.master.bind("<Escape>", self.exit_fullscreen)  # 绑定Esc键退出全屏
        self.master.bind("<space>", self.toggle_play_pause)  # 绑定空格键
        # 绑定数字键 1 和 2
        self.master.bind("<Key-1>", lambda event: self.set_audio_track(1))  # 原唱
        self.master.bind("<Key-3>", lambda event: self.set_audio_track(2))  # 伴唱

        # 绑定关闭事件
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        # 配置行和列的权重

        self.master.grid_rowconfigure(0, weight=1)

        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=2)
        self.master.grid_columnconfigure(2, weight=1)
        for i in range(9):
            self.controls_frame.grid_columnconfigure(i, weight=1)
        width = 800  # 设置窗口宽度
        height = 820  # 设置窗口高度
        x_position = 1000  # 设置窗口的左边距为1000像素
        y_position = 80

        # 设置窗口几何属性
        self.master.geometry(f"{width}x{height}+{x_position}+{y_position}")

        self.master.bind("<Left>", self.set_aspect_ratio_16_9)  # 左方向键设置为16:9
        self.master.bind("<Right>", self.set_default_aspect_ratio)  # 右方向键恢复默认比例
        self.master.bind("<Right>", self.set_default_aspect_ratio)  # 右方向键恢复默认比例
        self.master.bind("<Down>", self.play_next_song)
        self.master.bind("<Key-5>", lambda event: self.replay_video())  # 将按键5与重播功能绑定
        self.master.bind("<Key-6>", lambda event: self.fast_forward())  # 绑定右方向键为快进
        self.master.bind("<Key-4>", lambda event: self.rewind())  # 绑定左方向键为快退


        # 设置自定义图标
        self.master.iconbitmap('data/icon.ico')  # 确保这条路径指向你的图标文件

    def set_aspect_ratio_16_9(self, event=None):
        """设置视频显示比例为16:9"""
        self.player.video_set_aspect_ratio("16:9")  # 设置视频的显示比例为16:9
        print("视频显示比例已设置为 16:9")

    def set_default_aspect_ratio(self, event=None):
        """设置视频显示为默认比例"""
        self.player.video_set_aspect_ratio("4:3")  # 设置视频的显示比例为默认
        print("视频显示比例已恢复为默认")

    def add_local_video(self):
        """选择本地视频文件并添加到已点歌曲列表"""
        file_paths = filedialog.askopenfilenames(title="选择视频文件", filetypes=[("视频文件", "*.mp4;*.mkv;*.mpg;*.mov;*.ts;*.mp3;*.avi")])
        for file_path in file_paths:
            if file_path:  # 确保文件路径有效
                # 获取文件名用于显示
                song_name = os.path.basename(file_path)
                singer_name = "本地歌曲"  # 或者你可以添加其他方式来获取歌手名称
                self.add_to_played_song_list(file_path, song_name, singer_name)  # 添加到已点歌曲列表


    def toggle_fullscreen(self, event=None):
        if self.master.attributes('-fullscreen'):
            self.exit_fullscreen()
        else:
            self.master.attributes('-fullscreen', True)
            self.hide_controls()

    def exit_fullscreen(self, event=None):
        """退出全屏模式"""
        self.master.attributes('-fullscreen', False)
        self.show_controls()  # 重新显示控制元素（如果有需要）

    def hide_controls(self):
        """隐藏所有控制元素"""
        self.controls_frame.grid_remove()
        self.replay_button.grid_remove()
        self.pause_button.grid_remove()
        self.stop_button.grid_remove()
        self.next_button.grid_remove()
        self.original_button.grid_remove()
        self.伴唱_button.grid_remove()
        self.fullscreen_button.grid_remove()
        self.volume_scale.grid_remove()
        self.progress_scale.grid_remove()
        self.played_song_list_frame.grid_remove()  # 隐藏已点歌曲列表
        self.add_local_video_button.grid_remove()  # 隐藏添加本地视频按钮

    def show_controls(self):
        """重新显示所有控制元素"""
        self.controls_frame.grid()
        self.replay_button.grid()
        self.pause_button.grid()
        self.stop_button.grid()
        self.next_button.grid()
        self.original_button.grid()
        self.伴唱_button.grid()
        self.fullscreen_button.grid()
        self.volume_scale.grid()
        self.progress_scale.grid()
        self.played_song_list_frame.grid()  # 重新显示已点歌曲列表
        self.add_local_video_button.grid()  # 重新显示添加本地视频按钮


    def show_popup_menu(self, event):
        """显示右键菜单"""
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()

    def delete_selected_songs(self):
        """删除选中的歌曲"""
        selected_indices = self.played_song_listbox.curselection()
        for index in reversed(selected_indices):  # 从后往前删除，避免索引错乱
            self.played_song_listbox.delete(index)
            self.played_song_list.pop(index)

    def clear_played_song_list(self):
        """清空已点歌曲列表"""
        self.played_song_listbox.delete(0, tk.END)
        self.played_song_list.clear()

    def load_video(self, url):
        """加载并播放视频"""
        self.video_url = url
        media = self.Instance.media_new(self.video_url)
        self.player.set_media(media)
        self.player.set_hwnd(self.canvas.winfo_id())  # 设置视频在Canvas上播放
        self.player.play()  # 加载后立即播放

        self.player.audio_set_track(self.current_audio_track_index)  # 设置音轨为当前索引
        self.update_progress()  # 启动进度更新
        self.is_playing = True  # 标记当前为播放状态
        self.update_playing_song_background()  # 更新列表背景


    def add_directory(self):
        """选择目录并添加目录下的所有视频文件到已点歌曲列表"""
        directory_path = filedialog.askdirectory(title="选择视频目录")  # 选择目录
        if directory_path:  # 确保选择了目录
            # 遍历目录下的所有文件
            for filename in os.listdir(directory_path):
                if filename.endswith(('.mp4', '.mkv', '.avi', '.ts', '.mov''.mp3',)):  # 检查文件扩展名
                    file_path = os.path.join(directory_path, filename)  # 获取完整的文件路径
                    song_name = filename  # 可以根据需要修改，比如只取文件名部分
                    singer_name = "本地歌曲"  # 可以根据需要修改或添加歌手名称
                    self.add_to_played_song_list(file_path, song_name, singer_name)  # 添加到已点歌曲列表

    def add_to_played_song_list(self, url, song_name, singer_name):
        """将视频添加到已点歌曲列表"""
        if url not in self.played_song_list:
            self.played_song_list.append(url)  # 添加到已点歌曲列表
            self.played_song_listbox.insert(tk.END, f"{song_name} - {singer_name}")  # 在已点歌曲列表中显示歌曲名称和歌手名称

            # 检查已点列表是否为空，如果为空则自动播放
            if len(self.played_song_list) == 1:  # 如果这是第一首歌
                self.current_song_index = 0  # 更新当前歌曲索引
                self.load_video(url)  # 播放新添加的曲目
                self.player.audio_set_track(self.current_audio_track_index)  # 设置音轨为当前索引
                print(f"歌曲 '{song_name}' 添加到已点歌曲列表并开始播放")  # Debug信息


    def set_audio_track(self, track_index):
        """设置音轨并保存切换的音轨索引"""
        print(f"尝试切换到音轨: {track_index + 1}")  # 输出切换的目标音轨索引
        
        track_count = self.player.audio_get_track_count()  # 获取当前音轨数量
        print(f"当前音轨数量: {track_count}")  # 输出当前的音轨总数

        if track_index < track_count:  # 确保所选音轨在范围内
            self.player.audio_set_track(track_index)
            self.current_audio_track_index = track_index  # 更新当前音轨索引
            VideoPlayer.last_audio_track_index = track_index  # 记录最后一次切换的音轨索引
            print(f"已切换到音轨 {track_index + 1}")  # 输出当前切换的信息
            
            # 更新按钮颜色
            if track_index == 1:  # 原唱
                self.original_button.config(fg="green")
                self.伴唱_button.config(fg="black")
            elif track_index == 2:  # 伴唱
                self.伴唱_button.config(fg="green")
                self.original_button.config(fg="black")
        else:
            print(f"音轨索引 {track_index + 1} 超出范围，当前音轨数量为 {track_count}")  # 输出错误信息

    def start_seek(self, event):
        """开始拖动进度条时的处理"""
        self.is_seeking = True  # 设置标记为正在拖动

    def seek_video(self, event):
        """处理进度条释放事件，将视频时间设置为用户选择的时间"""
        progress = self.progress_scale.get()
        time_in_seconds = (self.player.get_length() * progress) / 100  # 计算时间
        self.player.set_time(int(time_in_seconds))  # 调整播放时间
        self.is_seeking = False  # 重置拖动标志

    def fast_forward(self):
        """快进10秒"""
        current_time = self.player.get_time()  # 获取当前播放时间
        new_time = current_time + 10000  # 增加10秒
        self.player.set_time(new_time)  # 设置新的播放时间
        print(f"快进至: {new_time // 1000}秒")

    def rewind(self):
        """快退10秒"""
        current_time = self.player.get_time()  # 获取当前播放时间
        new_time = max(0, current_time - 10000)  # 减少10秒，确保不为负
        self.player.set_time(new_time)  # 设置新的播放时间
        print(f"快退至: {new_time // 1000}秒")


    def play_next_song(self,event=None):
        """播放下一首歌曲"""
        # 从列表中移除当前播放的歌曲
        if self.current_song_index >= 0:
            self.played_song_listbox.delete(0)  # 删除当前播放的歌曲
            self.played_song_list.pop(0)  # 从列表中移除
            self.current_song_index -= 1  # 更新当前歌曲索引

        if self.current_song_index + 1 < len(self.played_song_list):
            self.current_song_index += 1  # 增加当前歌曲索引
            next_song_url = self.played_song_list[self.current_song_index]  # 获取下一首歌曲的URL
            self.load_video(next_song_url)  # 播放下一首歌曲
            print(f"切换到歌曲 '{next_song_url}'")  # 输出切换到的下一首歌曲
            
            # 等待视频开始播放后再切换音轨
            self.wait_for_video_to_play()  # 调用等待机制
        else:
        # 如果播放完所有歌曲，则重播当前歌曲
           self.replay_video()  # 调用重播功能


    def wait_for_video_to_play(self):
        """等待视频开始播放"""
        if self.player.is_playing():
            self.check_and_set_audio_track()  # 切换音轨
        else:
            self.master.after(1000, self.wait_for_video_to_play)  # 每秒检查一次


    def check_and_set_audio_track(self):
        """检查音轨数量并设置音轨"""
        track_count = self.player.audio_get_track_count()
        print(f"当前音轨数量: {track_count}")  # 输出当前音轨数量

        if track_count > 0:
            self.set_audio_track(VideoPlayer.last_audio_track_index)  # 使用最后切换的音轨索引
        else:
            print("没有可用的音轨，无法切换音轨。")  # 当没有音轨时提示信息

    def play_played_song(self, event):
        selected_index = self.played_song_listbox.curselection()
        if selected_index:
            # 获取所选已点歌曲的 URL 和歌曲名称
            video_url = self.played_song_list[selected_index[0]]
            song_name = self.played_song_listbox.get(selected_index[0])

            # 如果选择的歌曲不是正在播放的歌曲
            if selected_index[0] != self.current_song_index:
                # 将选中的歌曲置顶到列表的顶部
                self.played_song_listbox.delete(selected_index[0])  # 删除原有位置
                self.played_song_listbox.insert(0, song_name)  # 插入到顶部

                # 更新已点歌曲列表的索引
                self.played_song_list.remove(video_url)  # 先从列表中删除
                self.played_song_list.insert(0, video_url)  # 再插入到顶部

                # 更新当前歌曲索引
                self.current_song_index = 0  # 指向第一首

                # 在这里播放歌曲，并确保音轨使用当前音轨索引
                self.load_video(video_url)  # 播放选中的歌曲
                # 等待视频开始播放后再切换音轨
                self.wait_for_video_to_play()  # 调用等待机制

    def play_video(self):
        if self.video_url:
            self.player.play()
            self.is_playing = True  # 标记为正在播放
            self.update_playing_song_background()  # 更新列表背景
    def replay_video(self):
        """重播当前播放的视频"""
        if self.current_song_index >= 0:
            current_video_url = self.played_song_list[self.current_song_index]
            self.load_video(current_video_url)  # 重新加载并播放当前视频
            print(f"重播视频：'{current_video_url}'")  # Debug信息
            # 等待视频开始播放后再切换音轨
            self.wait_for_video_to_play()  # 调用等待机制

    def update_playing_song_background(self):
        # 清除所有歌曲的背景
        for i in range(len(self.played_song_listbox.get(0, tk.END))):
            self.played_song_listbox.itemconfig(i, {'bg': 'white'})  # 设置所有背景为白色

        # 设置当前播放歌曲的背景为蓝色
        if self.current_song_index >= 0:
            self.played_song_listbox.itemconfig(self.current_song_index, {'bg': 'lightblue'})  # 设置背景颜色

    def pause_video(self):
        self.player.pause()
        self.is_playing = False  # 标记为暂停状态
        self.update_playing_song_background()  # 更新列表背景

    def stop_video(self):
        self.player.stop()
        self.is_playing = False  # 标记为停止状态
        self.update_playing_song_background()  # 更新列表背景
    def toggle_play_pause(self, event=None):
        """切换播放和暂停"""
        if self.is_playing:
            self.pause_video()  # 如果当前正在播放，则调用暂停
        else:
            self.play_video()  # 否则调用播放



    def set_volume(self, event):
        volume = self.volume_scale.get()
        volume = max(0, min(volume, 100))  # 确保音量在0到100之间
        self.player.audio_set_volume(volume)


    def seek_video(self, event):
        progress = self.progress_scale.get()
        time_in_seconds = (self.player.get_length() * progress) / 100  # 计算时间
        self.player.set_time(int(time_in_seconds))  # 调整播放时间

    def update_progress(self):
        if self.video_url and self.player.is_playing():
            current_time = self.player.get_time()
            length = self.player.get_length()
            if length > 0:
                progress_percentage = (current_time / length) * 100
                self.progress_scale.set(progress_percentage)  # 更新进度条

            # 检查视频是否播放完毕，提前2秒切歌
            if self.player.get_state() == vlc.State.Ended or (length - current_time <= 2500):

                self.play_next_song()  # 自动播放下一首歌曲

        self.master.after(1000, self.update_progress)  # 每秒更新

    def on_close(self):
        self.stop_video()  # 确保视频停止
        VideoPlayer.current_instance = None  # 清空当前实例
        self.master.destroy()  # 关闭窗口
        
# 忽略不安全请求警告
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

def login():
    username = username_entry.get()
    password = password_entry.get()
    
    url = 'https://gitee.com/cclchuang/huang1897.github.io/raw/main/mm.txt'  
            
    try:
        response = requests.get(url, verify=False)  # 关闭SSL证书验证
        response.raise_for_status()  
        user_data = response.text.splitlines()  

        for line in user_data:
            user_info = line.strip().split(",")  
            if len(user_info) >= 5:
                db_username = user_info[0].strip()  
                db_password = user_info[1].strip()  
                registration_date_str = user_info[2].strip()  
                subscription_days = int(user_info[3].strip())  
                expiry_date_str = user_info[4].strip()  
                
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")

                if db_username == username and db_password == password:    
                    remaining_days = (expiry_date - datetime.now()).days  
                    
                    if remaining_days >= 0:
                        messagebox.showinfo("登录成功", f"欢迎登录！\n会员到期时间剩余: {remaining_days} 天")
                        
                        if remember_var.get():
                            save_login_info(username, password)
                        else:
                            save_login_info('', '')

                        login_window.destroy()
                        main_app()
                        return
                    
                    else:
                        messagebox.showerror("会员过期", "您的会员已过期，无法登录！")
                        return

        messagebox.showerror("登录失败", "用户名或密码错误！")
        
    except Exception as e:
        messagebox.showerror("请求失败", f"网络错误")


def clear_login_info():
    """清空登录信息的函数"""
    username_entry.delete(0, tk.END)  # 清空用户名输入框
    password_entry.delete(0, tk.END)  # 清空密码输入框
    remember_var.set(False)  # 取消记住密码复选框的选中状态
    
    # 清空登录信息配置
    save_login_info('', '')  # 重置登录信息为空

# 主应用程序的函数
def main_app():
    global db_path, download_directory, keyword, conversion_records, is_downloading, current_download_index, downloaded_files, rename_in_progress
    download_directory = '.'
    keyword = ""
    conversion_records = []

    db_path = os.path.join('data', 'itv.db')  # 修改为指向 data 目录中的数据库文件
    is_downloading = False  # 添加这一行
    current_download_index = 0  # 添加这一行
    downloaded_files = set()  # 初始化下载文件集合
    rename_in_progress = False  # 初始化重命名过程标志

    # 尝试从配置文件中读取数据库路径
    try:
        with open('db_config.json', 'r') as f:
            config = json.load(f)
            db_path = config['db_path']
    except (FileNotFoundError, json.JSONDecodeError):
        db_path = os.path.join('data', 'itv.db')  # 确保在未找到配置文件时也指向 data 目录

    # 尝试从配置文件中读取上次的下载目录，如果没有则默认为当前目录
    try:
        with open(os.path.join('data', 'download_config.json'), 'r') as f:  # 修改为指向 data 目录下的文件
            config = json.load(f)
            download_directory = config['directory']
    except (FileNotFoundError, json.JSONDecodeError):
        download_directory = '.'

    # 创建主窗口并居中显示
    root = tk.Tk()
    root.title("KTV 歌曲下载工具2.0")

    # 设置主窗口尺寸
    main_window_width = 760
    main_window_height = 660

    # 获取屏幕尺寸
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 计算窗口位置，横坐标设为0，纵坐标居中
    x = 150  # 设置窗口在屏幕左边
    y = (screen_height // 2) - (main_window_height // 2)

    # 设置窗口大小和位置
    root.geometry(f"{main_window_width}x{main_window_height}+{x}+{y}")
       # 设置主窗口图标
    root.iconbitmap('data/icon.ico')  # 替换为你的图标文件的相对路径


    def try_connect(url):
        try:
            urllib.request.urlopen(url)
            return url  # 返回有效链接
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # 尝试 720 版本
                url = url.replace("songs/", "songs/720/")
                try:
                    urllib.request.urlopen(url)  # 再次请求
                    return url  # 返回有效链接
                except urllib.error.URLError:
                    return None  # 连接失败
            else:
                return None  # 连接失败
        except Exception:
            return None  # 连接失败   

    # 下载函数

    def set_download_directory():
        new_directory = filedialog.askdirectory()
        if new_directory:
            global download_directory
            download_directory = new_directory
            with open(os.path.join('data', 'download_config.json'), 'w') as f:  # 修改为指向 data 目录下的文件
                json.dump({'directory': download_directory}, f)
            path_entry.delete(0, tk.END)
            path_entry.insert(0, download_directory)

    def open_download_directory():
        if os.path.exists(download_directory):
            os.startfile(download_directory)
        else:
                messagebox.showerror("错误", "下载目录不存在！")
    def get_song_number():
        """获取当前选择的歌曲或歌曲模块项目的编号"""
        selected_item = tree.selection()  # 获取当前选中的项
        if selected_item:
            item = tree.item(selected_item[0])  # 获取所选项的详细信息
            if item['tags'][0] == "song":
                # 从values中提取歌曲编号
                song_number = item['values'][3]  
                return song_number
            elif item['tags'][0] == "song_module_item":
                # 假设歌曲模块项的编号与歌曲模块项的值相同，您可以根据需要调整
                song_module_item_number = item['values'][3]  
                return song_module_item_number
        return None  # 如果没有选中项，返回None



    def search_data(event=None):
        global keyword
        new_keyword = entry.get()
        if new_keyword != keyword:
            keyword = new_keyword
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                # 查询歌曲信息，包括编号，并根据 temperature 降序排序
                query_song = f"""
                    SELECT name, number, singer_names, edition 
                    FROM song 
                    WHERE name LIKE '%{keyword}%' 
                    OR singer_names LIKE '%{keyword}%' 
                    OR edition LIKE '%{keyword}%' 
                    OR acronym LIKE '%{keyword}%'
                    ORDER BY temperature DESC  -- 根据 temperature 降序排序
                """
                cursor.execute(query_song)
                results_song = cursor.fetchall()

                # 查询歌曲模块项
                query_song_module_item = f"""
                        SELECT song_name, song_number FROM song_module_item 
                        WHERE song_name LIKE '%{keyword}%'
                    """
                cursor.execute(query_song_module_item)
                results_song_module_item = cursor.fetchall()
            

                # 清空现有数据
                tree.delete(*tree.get_children())

                # 更新搜索结果数量的标签
                number_of_songs = len(results_song) + len(results_song_module_item)  # 计算歌曲总数
                search_result_label.config(text=f"搜索到的歌曲数量: {number_of_songs}")  # 更新标签文本

                for result in results_song:
                    # 假设result[1]是歌曲编号
                    tree.insert("", tk.END, text="歌曲", values=(result[0], result[2], result[3], result[1]), tags=("song"))

                # 更新列设置，让编号这一列不可见
                tree["columns"] = ("歌曲名称", "歌手名称", "版本信息", "编号")  # 增加编号列
                tree.heading("#0", text="类型")
                tree.heading("歌曲名称", text="歌曲名称")
                tree.heading("歌手名称", text="歌手名称")
                tree.heading("版本信息", text="版本信息")
                tree.column("编号", width=0, stretch=tk.NO)  # 让编号列宽度为0，隐藏
                tree.tag_configure("song", background="lightblue")

                # 插入歌曲模块项结果
                for result in results_song_module_item:
                    tree.insert("", tk.END, text="歌曲模块项", values=(result[0], "", "", result[1]), tags=("song_module_item"))
                tree.tag_configure("song_module_item", background="lightgreen")

                # 调整列宽
                for col in ("歌曲名称", "歌手名称", "版本信息"):
                    tree.column(col, width=100)  # 设置每列的固定宽度为100像素

            except sqlite3.OperationalError as e:
                tk.messagebox.showinfo("提示", f"错误：数据库可能不存在: {e}")

                
    def play_selected_song(event):
        song_number = get_song_number()  # 获取歌曲编号
        if song_number is not None:
            item = tree.item(tree.selection()[0])  # 选中项
            song_name = item['values'][0]  # 获取歌曲名称
            singer_name = item['values'][1]  # 获取歌手名称
            
            video_url = f"http://txysong.mysoto.cc/songs/{song_number}.mkv"  # 使用编码构建视频链接

            
            # 尝试连接原始链接
            valid_url = try_connect(video_url)
            
            if valid_url:
                if VideoPlayer.current_instance is None:
                    # 如果没有打开的播放器，创建一个新的播放器
                    video_window = tk.Toplevel()
                    video_window.focus_force()  # 确保窗口获得焦点
                    player = VideoPlayer(video_window)
                    player.add_to_played_song_list(valid_url, song_name, singer_name)  # 添加到已点歌曲列表并播放
                else:
                    # 如果播放器已存在，直接将歌曲添加到已点歌曲列表
                    VideoPlayer.current_instance.add_to_played_song_list(valid_url, song_name, singer_name)
            else:
                tk.messagebox.showinfo("播放失败", f"无法播放视频链接：{video_url}，请检查连接是否有效。")


    # 下载部分
    current_download_index = 0  # 确保该变量定义在这里
    is_downloading = False  # 确保该变量定义在这里
    downloaded_files = set()  # 确保该变量定义在这里

    def download():
        global current_download_index, is_downloading
        if is_downloading:
            tk.messagebox.showinfo("提示", "当前文件正在下载中，请稍后再下载。")
            return
        
        selected_indices = tree.selection()
        if selected_indices:
            total_files = len(selected_indices)
            current_download_index = 0
            is_downloading = True
            start_next_download(total_files, selected_indices)
        else:
            tk.messagebox.showinfo("提示", "请先选择要下载的歌曲。")

    def start_next_download(total_files, selected_indices):
        """开始下一个下载任务"""
        global current_download_index
        if current_download_index < total_files:
            # 根据当前索引获取对应的选中歌曲编号
            selected_song_index = selected_indices[current_download_index]
            item = tree.item(selected_song_index)  # 获取对应的树状视图项
            song_number = item['values'][3]  # 假设第四列是歌曲编号
            url = f"http://txysong.mysoto.cc/songs/{song_number}.mkv"
            final_url = try_connect(url)
            if final_url:
                threading.Thread(target=download_file_with_progress, args=(final_url, total_files, selected_indices)).start()
            else:
                tk.messagebox.showerror("网络连接错误", f"无法连接到 {url}。")
                current_download_index += 1
                start_next_download(total_files, selected_indices)
        else:
            global is_downloading
            is_downloading = False
            tk.messagebox.showinfo("提示", "所有文件下载完成")


    def download_file_with_progress(url, total_files, selected_indices):
        global current_download_index, is_downloading, downloaded_files  # 确保声明全局变量
        local_filename = url.split('/')[-1]

        if local_filename in downloaded_files:
            tk.messagebox.showinfo("提示", f"{local_filename}已下载，无需重复下载。")
            current_download_index += 1
            start_next_download(total_files, selected_indices)
            return

        out_file = None  # 初始化 out_file 为 None，以便后续检查
        try:
            response = requests.get(url, stream=True)  # 使用requests获取内容，stream参数为True以便逐块下载
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            block_size = 1024
            item = tree.item(selected_indices[current_download_index])
            song_name = item['values'][0]
            label_name.config(text=f"正在下载：{song_name}", fg="black")

            out_file = open(os.path.join(download_directory, local_filename), 'wb')
            
            for buffer in response.iter_content(chunk_size=block_size):  # 逐块写入文件
                if not buffer:
                    break
                out_file.write(buffer)
                downloaded += len(buffer)

                # 每0.5秒更新一次UI
                if downloaded % (block_size * 10) == 0:  # 每10个块更新
                    progress = downloaded / total_size * 100
                    root.after(0, lambda p=progress: update_progress_ui(p, song_name, total_files))
            
            downloaded_files.add(local_filename)

        except Exception as e:
            print(f"下载过程中出现错误：{e}")
            label_name.config(text=f"下载错误：{song_name}", fg="red")

        finally:
            if out_file is not None:
                out_file.close()

        current_download_index += 1
        start_next_download(total_files, selected_indices)
        auto_rename_song_file(os.path.join(download_directory, local_filename))
        label_name.config(text=f"下载完成：{song_name}", fg="green")

    def update_progress_ui(progress, song_name, total_files):
        """更新进度条和标签的UI函数"""
        progress_bar['value'] = progress
        label_name.config(text=f"正在下载：{song_name}（总文件数: {total_files}）")

    def auto_rename_song_file(full_path):
        if not os.path.exists(full_path):
            print(f"文件路径 {full_path} 不存在。")
            return

        filename = os.path.basename(full_path)
        number = filename.split('.')[0]

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT number, singer_names, name, edition FROM song UNION ALL SELECT song_number, '', song_name, '' FROM song_module_item")
        records = cursor.fetchall()

        found_match = False
        for record in records:
            db_number, singer, song_name, edition = record
            if str(number) == str(db_number):
                found_match = True
                new_filename = f"{singer}_{song_name}_{edition}.mkv" if edition else f"{singer}_{song_name}.mkv"
                new_full_path = os.path.join(os.path.dirname(full_path), new_filename)
                if os.path.exists(full_path) and not os.path.exists(new_full_path):
                    os.rename(full_path, new_full_path)
                    record_conversion(full_path, new_full_path)
                    break

        if not found_match:
            print(f"未找到与文件编号 {number} 匹配的数据库记录，无法自动命名文件 {full_path}。")

        conn.close()

    def record_conversion(old_filename, new_filename):
        conversion_records.append((old_filename, new_filename))

    def open_ktv_player():
        """打开KTV点歌器的函数，只允许一个实例"""
        if VideoPlayer.current_instance is None:
            video_window = tk.Toplevel()
            player = VideoPlayer(video_window)
        else:
            messagebox.showinfo("提示", "KTV点歌器已经打开。")  # 提示用户已经打开
    def get_song_count():
        """获取数据库中 song 表和 song_module_item 表的歌曲总数"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 查询 song 表中的歌曲总数
            cursor.execute("SELECT COUNT(*) FROM song")
            song_count = cursor.fetchone()[0]

            # 查询 song_module_item 表中的歌曲总数
            cursor.execute("SELECT COUNT(*) FROM song_module_item")
            module_item_count = cursor.fetchone()[0]

            # 计算总的歌曲数量
            total_count = song_count + module_item_count
            
            conn.close()
            return total_count
        except Exception as e:
            print(f"获取曲库数量出现错误: {e}")
            return 0  # 返回0表示没有获取到数量

    # 创建一个主框架用于组织界面元素
    main_frame = ttk.Frame(root)
    main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    # 配置行和列的权重，使其可以随窗口变动
    main_frame.grid_rowconfigure(0, weight=0)  # 第一行用于标签
    main_frame.grid_rowconfigure(1, weight=0)  # 第二行用于输入框和搜索按钮
    main_frame.grid_rowconfigure(2, weight=2)  # 第三行用于Treeview
    main_frame.grid_rowconfigure(3, weight=0)  # 第四行用于设置路径和下载按钮
    main_frame.grid_rowconfigure(4, weight=0)  # 第五行用于打开目录按钮
    main_frame.grid_rowconfigure(5, weight=0)  # 第六行用于KTV点歌器按钮

    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=2)
    main_frame.grid_columnconfigure(2, weight=0)


    label_instructions = ttk.Label(main_frame, text="请输入歌名或歌手名：")
    label_instructions.config(font=('Helvetica', 14, 'bold'), foreground='green')
    label_instructions.grid(row=0, column=1, padx=180, pady=5, sticky='nsew')  # 使用 'nsew' 使其在上下左右都居中

    entry = ttk.Entry(main_frame)
    entry.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
    entry.bind("<Return>", search_data)

    button = ttk.Button(main_frame, text="搜索", command=search_data)
    button.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

    # 创建 Treeview
    tree = ttk.Treeview(main_frame, selectmode='extended', show='headings', columns=("歌曲名称", "歌手名称", "版本信息"))
    for col in ("歌曲名称", "歌手名称", "版本信息"):
        tree.heading(col, text=col)
        tree.column(col, stretch=tk.YES)  # 设置合适的宽度
    tree.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')  # 修改此行

    # 添加滚动条
    scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=2, column=2, sticky='ns')  # 修改此行

    tree.bind("<Double-1>", play_selected_song)  # 绑定双击事件

    # 设置按钮和输入框的行
    set_directory_button = ttk.Button(main_frame, text="选择下载目录", command=set_download_directory)
    set_directory_button.grid(row=3, column=0, padx=10, pady=10, sticky='ew')

    path_entry = ttk.Entry(main_frame, width=80)
    path_entry.insert(0, download_directory)
    path_entry.grid(row=3, column=1, padx=(10, 5), pady=10, sticky='ew')

    download_button = ttk.Button(main_frame, text="下载", command=download)
    download_button.grid(row=4, column=0, padx=10, pady=10, sticky='ew')
      # 创建打开 KTV 点歌器 按钮
    open_ktv_button = ttk.Button(main_frame, text="打开KTV点歌器", command=open_ktv_player)
    open_ktv_button.grid(row=4, column=1, padx=10, pady=10, sticky='ew')

    open_directory_button = ttk.Button(main_frame, text="打开下载目录", command=open_download_directory)
    open_directory_button.grid(row=5, column=0, padx=10, pady=10, sticky='ew')
        # 在 main_app 函数中添加
    search_result_label = ttk.Label(main_frame, text="搜索到的歌曲数量: 0")
        # 在 main_app 函数中调用并更新标签文本
    total_songs = get_song_count()  # 获取当前曲库中的歌曲数量
    search_result_label.config(text=f"当前曲库歌曲数量: {total_songs}")  # 更新标签文本
    search_result_label.grid(row=5, column=1, padx=10, pady=10, sticky='ew')
    # 进度条和标签
    progress_bar = ttk.Progressbar(root, length=500, mode='determinate')
    progress_bar.pack(pady=20)

    label_name = tk.Label(root, text="")
    label_name.pack()

    progress_label = tk.Label(root, text="")
    progress_label.pack()

    # 设置样式
    style = ttk.Style()
    style.theme_use('vista')
    style.configure("custom.Horizontal.TProgressbar", thickness=20, troughcolor='gray', background='green')
    style.map("custom.Horizontal.TProgressbar", background=[('active', 'green')])

    root.protocol("WM_DELETE_WINDOW", lambda: sys.exit())  # 关闭时退出程序
    root.mainloop()

# 创建登录界面
login_window = tk.Tk()
login_window.title("登录")

 # 替换为你的图标文件的相对路径
# 设置窗口尺寸
login_window_width = 300
login_window_height = 180

# 获取屏幕尺寸
screen_width = login_window.winfo_screenwidth()
screen_height = login_window.winfo_screenheight()

# 计算窗口位置
x = (screen_width // 2) - (login_window_width // 2)
y = (screen_height // 2) - (login_window_height // 2)

# 设置窗口大小和位置
login_window.geometry(f"{login_window_width}x{login_window_height}+{x}+{y}")

username_label = ttk.Label(login_window, text="用户名:")
username_label.pack()
username_entry = ttk.Entry(login_window)
username_entry.pack()

password_label = ttk.Label(login_window, text="密码:")
password_label.pack()
password_entry = ttk.Entry(login_window, show='*')  
password_entry.pack()

remember_var = tk.BooleanVar()
remember_checkbox = ttk.Checkbutton(login_window, text="记住密码", variable=remember_var)
remember_checkbox.pack()

login_button = ttk.Button(login_window, text="登录", command=login)
login_button.pack()

# 清空登录信息按钮
clear_button = ttk.Button(login_window, text="清空登录", command=clear_login_info)
clear_button.pack()

    # 添加检测更新按钮
update_button = ttk.Button(login_window, text="检测更新", command=check_for_updates)
update_button.pack()
# 设置自定义图标
login_window.iconbitmap('data/icon.ico') 
login_info = load_login_info()

if login_info:
    username_entry.insert(0, login_info.get('username', ''))
    password_entry.insert(0, login_info.get('password', ''))
    remember_var.set(True)

login_window.protocol("WM_DELETE_WINDOW", lambda: sys.exit())  # 关闭时退出程序
login_window.mainloop()
