import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
from urllib.parse import urljoin
import threading
import re
import logging
from datetime import datetime
import chardet
import time

class WebsiteCrawler:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("网站爬虫工具-OE源码网")
        self.window.geometry("900x700")
        self.window.configure(bg="#f0f0f0")
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("微软雅黑", 10))
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TEntry", font=("微软雅黑", 10))
        self.style.configure("TCombobox", font=("微软雅黑", 10))
        self.style.configure("Header.TLabel", font=("微软雅黑", 14, "bold"), background="#f0f0f0")
        self.style.configure("Stop.TButton", font=("微软雅黑", 10, "bold"), foreground="red")
        self.style.configure("Help.TButton", font=("微软雅黑", 9), foreground="blue")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.window, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        header_label = ttk.Label(self.main_frame, text="网站爬虫工具-2oe.cn", style="Header.TLabel")
        header_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 创建输入区域框架
        input_frame = ttk.Frame(self.main_frame)
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # URL输入
        ttk.Label(input_frame, text="目标网站URL:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.url_entry = ttk.Entry(input_frame, width=50)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # 保存路径
        ttk.Label(input_frame, text="保存路径:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.save_path_entry = ttk.Entry(input_frame, width=50)
        self.save_path_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        self.save_path_entry.insert(0, os.path.join(os.getcwd(), "downloaded_sites"))
        
        # 浏览按钮
        browse_button = ttk.Button(input_frame, text="浏览...", command=self.browse_save_path)
        browse_button.grid(row=1, column=2, padx=5)
        
        # 创建选项区域框架
        options_frame = ttk.Frame(self.main_frame)
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 爬取深度
        ttk.Label(options_frame, text="爬取深度:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.depth_var = tk.StringVar(value="2")
        self.depth_entry = ttk.Entry(options_frame, textvariable=self.depth_var, width=5)
        self.depth_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # 深度帮助按钮
        depth_help = ttk.Button(options_frame, text="?", width=2, style="Help.TButton", command=lambda: self.show_help("爬取深度", "爬取深度决定了爬虫会递归爬取多少层链接。\n1表示只爬取当前页面\n2表示爬取当前页面及其直接链接的页面\n3及以上表示继续递归爬取"))
        depth_help.grid(row=0, column=2, sticky=tk.W, padx=2)
        
        # 编码选择
        ttk.Label(options_frame, text="默认编码:").grid(row=0, column=3, sticky=tk.W, padx=5)
        self.encoding_var = tk.StringVar(value="utf-8")
        self.encoding_combo = ttk.Combobox(options_frame, textvariable=self.encoding_var, width=10)
        self.encoding_combo['values'] = ('utf-8', 'gbk', 'gb2312', 'gb18030', 'auto')
        self.encoding_combo.grid(row=0, column=4, sticky=tk.W, padx=5)
        
        # 编码帮助按钮
        encoding_help = ttk.Button(options_frame, text="?", width=2, style="Help.TButton", command=lambda: self.show_help("默认编码", "设置网页的默认编码方式。\n如果选择'auto'，程序会自动检测网页编码。\n如果网页显示乱码，可以尝试切换不同的编码方式。"))
        encoding_help.grid(row=0, column=5, sticky=tk.W, padx=2)
        
        # 爬取模式
        ttk.Label(options_frame, text="爬取模式:").grid(row=0, column=6, sticky=tk.W, padx=5)
        self.crawl_mode_var = tk.StringVar(value="整站爬取")
        self.crawl_mode_combo = ttk.Combobox(options_frame, textvariable=self.crawl_mode_var, width=10)
        self.crawl_mode_combo['values'] = ('单页爬取', '整站爬取', '仅爬取图片')
        self.crawl_mode_combo.grid(row=0, column=7, sticky=tk.W, padx=5)
        self.crawl_mode_combo.bind('<<ComboboxSelected>>', self.on_crawl_mode_change)
        
        # 爬取模式帮助按钮
        mode_help = ttk.Button(options_frame, text="?", width=2, style="Help.TButton", command=lambda: self.show_help("爬取模式", "单页爬取：只爬取当前页面及其资源\n整站爬取：爬取整个网站的所有页面和资源\n仅爬取图片：只下载网站中的图片资源"))
        mode_help.grid(row=0, column=8, sticky=tk.W, padx=2)
        
        # 下载选项
        ttk.Label(options_frame, text="下载选项:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.download_html_var = tk.BooleanVar(value=True)
        self.download_css_var = tk.BooleanVar(value=True)
        self.download_js_var = tk.BooleanVar(value=True)
        self.download_img_var = tk.BooleanVar(value=True)
        
        html_check = ttk.Checkbutton(options_frame, text="HTML", variable=self.download_html_var)
        html_check.grid(row=1, column=1, padx=2, pady=5)
        
        css_check = ttk.Checkbutton(options_frame, text="CSS", variable=self.download_css_var)
        css_check.grid(row=1, column=2, padx=2, pady=5)
        
        js_check = ttk.Checkbutton(options_frame, text="JS", variable=self.download_js_var)
        js_check.grid(row=1, column=3, padx=2, pady=5)
        
        img_check = ttk.Checkbutton(options_frame, text="图片", variable=self.download_img_var)
        img_check.grid(row=1, column=4, padx=2, pady=5)
        
        # 下载选项帮助按钮
        download_help = ttk.Button(options_frame, text="?", width=2, style="Help.TButton", command=lambda: self.show_help("下载选项", "选择要下载的资源类型：\nHTML：网页的HTML文件\nCSS：样式表文件\nJS：JavaScript脚本文件\n图片：网站中的图片资源"))
        download_help.grid(row=1, column=5, sticky=tk.W, padx=2, pady=5)
        
        # 高级选项
        ttk.Label(options_frame, text="高级选项:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        # 请求延迟
        ttk.Label(options_frame, text="请求延迟(秒):").grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.delay_var = tk.StringVar(value="0.5")
        self.delay_entry = ttk.Entry(options_frame, textvariable=self.delay_var, width=5)
        self.delay_entry.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        # 延迟帮助按钮
        delay_help = ttk.Button(options_frame, text="?", width=2, style="Help.TButton", command=lambda: self.show_help("请求延迟", "每次请求之间的延迟时间，单位为秒。\n增加延迟可以减轻对目标服务器的压力，避免被封IP。\n建议值：0.5-2秒"))
        delay_help.grid(row=2, column=3, sticky=tk.W, padx=2, pady=5)
        
        # 超时设置
        ttk.Label(options_frame, text="超时(秒):").grid(row=2, column=4, sticky=tk.W, padx=5, pady=5)
        self.timeout_var = tk.StringVar(value="15")
        self.timeout_entry = ttk.Entry(options_frame, textvariable=self.timeout_var, width=5)
        self.timeout_entry.grid(row=2, column=5, sticky=tk.W, padx=5, pady=5)
        
        # 超时帮助按钮
        timeout_help = ttk.Button(options_frame, text="?", width=2, style="Help.TButton", command=lambda: self.show_help("超时设置", "请求超时时间，单位为秒。\n如果请求超过此时间没有响应，将视为失败。\n建议值：10-30秒"))
        timeout_help.grid(row=2, column=6, sticky=tk.W, padx=2, pady=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.main_frame, length=800, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=3, pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        # 开始按钮
        self.start_button = ttk.Button(button_frame, text="开始爬取", command=self.start_crawling)
        self.start_button.grid(row=0, column=0, padx=10)
        
        # 停止按钮
        self.stop_button = ttk.Button(button_frame, text="停止爬取", command=self.stop_crawling, style="Stop.TButton", state='disabled')
        self.stop_button.grid(row=0, column=1, padx=10)
        
        # 帮助按钮
        help_button = ttk.Button(button_frame, text="使用帮助", command=self.show_general_help)
        help_button.grid(row=0, column=2, padx=10)
        
        # 日志显示区域
        log_frame = ttk.Frame(self.main_frame)
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        ttk.Label(log_frame, text="爬取日志:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=100, font=("Consolas", 9))
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态标签
        self.status_label = ttk.Label(self.main_frame, text="")
        self.status_label.grid(row=6, column=0, columnspan=3)
        
        # 配置网格权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(5, weight=1)
        input_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        
        # 初始化日志
        self.setup_logging()
        
        # 计数器
        self.total_files = 0
        self.downloaded_files = 0
        
        # 已访问的URL集合
        self.visited_urls = set()
        
        # 爬取控制
        self.is_crawling = False
        self.should_stop = False
        
        # 添加窗口关闭事件处理
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_crawl_mode_change(self, event):
        mode = self.crawl_mode_var.get()
        if mode == "单页爬取":
            self.depth_var.set("1")
            self.depth_entry.config(state='disabled')
        elif mode == "整站爬取":
            self.depth_entry.config(state='normal')
        elif mode == "仅爬取图片":
            self.download_html_var.set(False)
            self.download_css_var.set(False)  # 禁用CSS下载
            self.download_js_var.set(False)   # 禁用JS下载
            self.download_img_var.set(True)
            # 禁用CSS和JS的复选框
            for widget in self.main_frame.winfo_children():
                if isinstance(widget, ttk.Checkbutton):
                    if widget.cget("text") in ["CSS", "JS"]:
                        widget.config(state='disabled')
            
    def browse_save_path(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path_entry.delete(0, tk.END)
            self.save_path_entry.insert(0, path)
        
    def setup_logging(self):
        # 创建logs目录
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # 设置日志文件名（使用当前时间）
        log_filename = f'logs/crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
    def log(self, message, level='info'):
        # 在GUI中显示日志
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        
        # 同时写入日志文件
        if level == 'error':
            logging.error(message)
        else:
            logging.info(message)
            
    def update_progress(self):
        if self.total_files > 0:
            progress = (self.downloaded_files / self.total_files) * 100
            self.progress['value'] = progress
            self.status_label.config(text=f"进度: {self.downloaded_files}/{self.total_files} 文件 ({progress:.1f}%)")
            
    def detect_encoding(self, content):
        # 使用chardet检测编码
        result = chardet.detect(content)
        return result['encoding']
        
    def start_crawling(self):
        url = self.url_entry.get().strip()
        save_path = self.save_path_entry.get().strip()
        try:
            depth = int(self.depth_var.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的爬取深度")
            return
            
        if not url:
            messagebox.showerror("错误", "请输入目标网站URL")
            return
            
        if not save_path:
            messagebox.showerror("错误", "请输入保存路径")
            return
            
        # 验证URL格式
        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("错误", "URL必须以http://或https://开头")
            return
            
        # 设置爬取状态
        self.is_crawling = True
        self.should_stop = False
        
        # 更新UI状态
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress['value'] = 0
        self.log_text.delete(1.0, tk.END)
        self.total_files = 0
        self.downloaded_files = 0
        self.visited_urls = set()
        
        # 记录爬取参数
        self.log(f"开始爬取网站: {url}")
        self.log(f"保存路径: {save_path}")
        self.log(f"爬取深度: {depth}")
        self.log(f"爬取模式: {self.crawl_mode_var.get()}")
        self.log(f"默认编码: {self.encoding_var.get()}")
        self.log(f"下载选项: HTML={self.download_html_var.get()}, CSS={self.download_css_var.get()}, JS={self.download_js_var.get()}, 图片={self.download_img_var.get()}")
        self.log(f"请求延迟: {self.delay_var.get()}秒")
        self.log(f"超时设置: {self.timeout_var.get()}秒")
        
        # 在新线程中运行爬虫
        thread = threading.Thread(target=self.crawl_website, args=(url, save_path, depth))
        thread.daemon = True
        thread.start()
        
    def stop_crawling(self):
        if self.is_crawling:
            self.should_stop = True
            self.log("正在停止爬取...", 'error')
            self.stop_button.config(state='disabled')
            
    def crawl_website(self, url, save_path, depth):
        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path)
                
            self.download_page(url, save_path, depth)
            
            if not self.should_stop:
                self.window.after(0, self.crawling_complete)
            else:
                self.window.after(0, self.crawling_stopped)
        except Exception as e:
            self.window.after(0, lambda: self.show_error(str(e)))
            
    def download_page(self, url, save_path, depth):
        if depth <= 0 or url in self.visited_urls or self.should_stop:
            return
            
        self.visited_urls.add(url)
            
        try:
            self.log(f"正在下载页面: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # 获取超时设置
            try:
                timeout = float(self.timeout_var.get())
            except ValueError:
                timeout = 15
                
            # 添加重试机制
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries and not self.should_stop:
                try:
                    response = requests.get(url, headers=headers, timeout=timeout)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise
                    self.log(f"下载页面失败，正在重试 ({retry_count}/{max_retries}): {url}", 'error')
                    time.sleep(2)  # 重试前等待2秒
            
            # 检测编码
            content = response.content
            detected_encoding = self.detect_encoding(content)
            if self.encoding_var.get() == 'auto':
                encoding = detected_encoding or 'utf-8'
            else:
                encoding = self.encoding_var.get()
                
            self.log(f"检测到编码: {detected_encoding}, 使用编码: {encoding}")
            
            # 解析HTML
            html_content = content.decode(encoding, errors='ignore')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 获取域名
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc
            if not domain:
                domain = "unknown_domain"
            
            # 保存HTML
            if self.download_html_var.get():
                path = parsed_url.path
                
                if not path or path.endswith('/'):
                    path = path + 'index.html'
                elif '.' not in path.split('/')[-1]:
                    path = path + '/index.html'
                    
                file_path = os.path.join(save_path, domain, path.lstrip('/'))
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(html_content)
                    
                self.total_files += 1
                self.downloaded_files += 1
                self.window.after(0, self.update_progress)
                self.log(f"已保存页面: {file_path}")
            
            # 下载资源文件
            self.download_resources(soup, url, save_path, domain)
            
            # 递归爬取链接
            if depth > 1 and not self.should_stop:
                # 获取请求延迟
                try:
                    delay = float(self.delay_var.get())
                except ValueError:
                    delay = 0.5
                    
                for link in soup.find_all('a'):
                    if self.should_stop:
                        break
                        
                    href = link.get('href')
                    if href:
                        absolute_url = urljoin(url, href)
                        if self.is_same_domain(url, absolute_url) and absolute_url not in self.visited_urls:
                            # 添加延迟，避免请求过快
                            time.sleep(delay)
                            self.download_page(absolute_url, save_path, depth - 1)
                            
        except requests.exceptions.RequestException as e:
            self.log(f"下载页面失败 {url}: {str(e)}", 'error')
        except Exception as e:
            self.log(f"处理页面失败 {url}: {str(e)}", 'error')
            
    def download_resources(self, soup, base_url, save_path, domain):
        # 下载CSS
        if self.download_css_var.get() and not self.should_stop:
            for css in soup.find_all(['link', 'style']):
                if self.should_stop:
                    break
                    
                if css.name == 'link' and css.get('rel') == ['stylesheet']:
                    href = css.get('href')
                    if href:
                        self.download_resource(urljoin(base_url, href), save_path, domain, 'CSS')
                elif css.name == 'style' and css.string:
                    # 处理内联样式中的背景图片
                    bg_matches = re.finditer(r'url\([\'"]?(.*?)[\'"]?\)', css.string)
                    for match in bg_matches:
                        if self.should_stop:
                            break
                            
                        bg_url = match.group(1)
                        if not bg_url.startswith('data:'):
                            self.download_resource(urljoin(base_url, bg_url), save_path, domain, 'CSS背景图片')
                    
        # 下载JavaScript
        if self.download_js_var.get() and not self.should_stop:
            for script in soup.find_all('script', src=True):
                if self.should_stop:
                    break
                    
                src = script.get('src')
                if src:
                    self.download_resource(urljoin(base_url, src), save_path, domain, 'JavaScript')
                    
        # 下载图片
        if self.download_img_var.get() and not self.should_stop:
            # 处理各种图片标签和属性
            img_sources = []
            
            # 1. 处理img标签
            for img in soup.find_all('img'):
                if self.should_stop:
                    break
                    
                # 处理src属性
                src = img.get('src')
                if src:
                    img_sources.append(src)
                    
                # 处理data-src属性（懒加载）
                data_src = img.get('data-src')
                if data_src:
                    img_sources.append(data_src)
                    
                # 处理data-original属性（懒加载）
                data_original = img.get('data-original')
                if data_original:
                    img_sources.append(data_original)
                    
                # 处理srcset属性（响应式图片）
                srcset = img.get('srcset')
                if srcset:
                    for src_str in srcset.split(','):
                        src_parts = src_str.strip().split(' ')
                        if src_parts:
                            img_sources.append(src_parts[0])
            
            # 2. 处理picture标签
            for picture in soup.find_all('picture'):
                if self.should_stop:
                    break
                    
                # 处理source标签
                for source in picture.find_all('source'):
                    srcset = source.get('srcset')
                    if srcset:
                        for src_str in srcset.split(','):
                            src_parts = src_str.strip().split(' ')
                            if src_parts:
                                img_sources.append(src_parts[0])
            
            # 3. 处理背景图片
            for tag in soup.find_all(True):  # 查找所有标签
                if self.should_stop:
                    break
                    
                # 处理style属性
                style = tag.get('style', '')
                if style:
                    bg_matches = re.finditer(r'background(?:-image)?:\s*url\([\'"]?(.*?)[\'"]?\)', style)
                    for match in bg_matches:
                        bg_url = match.group(1)
                        if not bg_url.startswith('data:'):
                            img_sources.append(bg_url)
            
            # 4. 处理CSS文件中的背景图片
            if self.download_css_var.get() and not self.should_stop:
                for css in soup.find_all('link', rel='stylesheet'):
                    if self.should_stop:
                        break
                        
                    href = css.get('href')
                    if href:
                        try:
                            css_url = urljoin(base_url, href)
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                            }
                            
                            # 获取超时设置
                            try:
                                timeout = float(self.timeout_var.get())
                            except ValueError:
                                timeout = 15
                                
                            response = requests.get(css_url, headers=headers, timeout=timeout)
                            response.raise_for_status()
                            
                            # 查找所有图片URL
                            css_text = response.text
                            # 匹配url()
                            bg_matches = re.finditer(r'url\([\'"]?(.*?)[\'"]?\)', css_text)
                            for match in bg_matches:
                                if self.should_stop:
                                    break
                                    
                                bg_url = match.group(1)
                                if not bg_url.startswith('data:'):
                                    img_sources.append(bg_url)
                                    
                            # 匹配@import
                            import_matches = re.finditer(r'@import\s+[\'"]([^\'"]+)[\'"]', css_text)
                            for match in import_matches:
                                if self.should_stop:
                                    break
                                    
                                import_url = match.group(1)
                                if not import_url.startswith('data:'):
                                    img_sources.append(import_url)
                                    
                        except Exception as e:
                            self.log(f"处理CSS文件失败 {css_url}: {str(e)}", 'error')
            
            # 下载所有找到的图片
            for src in set(img_sources):  # 使用set去重
                if self.should_stop:
                    break
                    
                if src and not src.startswith(('data:', 'about:', 'javascript:')):
                    try:
                        full_url = urljoin(base_url, src)
                        self.download_resource(full_url, save_path, domain, '图片')
                    except Exception as e:
                        self.log(f"处理图片URL失败 {src}: {str(e)}", 'error')
                        
    def download_resource(self, url, save_path, domain, resource_type):
        if self.should_stop:
            return
            
        try:
            # 跳过无效URL
            if not url or url.startswith(('data:', 'about:', 'javascript:')):
                return
                
            # 规范化URL
            url = url.strip()
            if url.startswith('//'):
                url = 'https:' + url
                
            # 检查是否已下载
            if url in self.visited_urls:
                return
            self.visited_urls.add(url)
                
            self.log(f"正在下载{resource_type}: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': url
            }
            
            # 添加特定的Accept头
            if resource_type == '图片':
                headers['Accept'] = 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
            elif resource_type == 'CSS':
                headers['Accept'] = 'text/css,*/*;q=0.1'
            elif resource_type == 'JavaScript':
                headers['Accept'] = 'text/javascript,application/javascript,*/*;q=0.1'
                
            # 获取超时设置
            try:
                timeout = float(self.timeout_var.get())
            except ValueError:
                timeout = 15
                
            # 添加重试机制
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries and not self.should_stop:
                try:
                    response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise
                    self.log(f"下载{resource_type}失败，正在重试 ({retry_count}/{max_retries}): {url}", 'error')
                    time.sleep(2)  # 重试前等待2秒
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            
            # 处理文件路径
            parsed_url = urllib.parse.urlparse(url)
            path = parsed_url.path
            
            if not path or path.endswith('/'):
                # 从Content-Type和URL生成文件名
                ext = self.get_extension_from_content_type(content_type, url)
                path = path + 'index' + ext
                
            # 处理查询参数
            if '?' in url and not path.endswith(('.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')):
                ext = self.get_extension_from_content_type(content_type, url)
                path = path + ext
                
            file_path = os.path.join(save_path, domain, path.lstrip('/'))
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 保存文件
            if resource_type in ['CSS', 'JavaScript']:
                content = response.content
                detected_encoding = self.detect_encoding(content)
                encoding = detected_encoding or 'utf-8'
                
                with open(file_path, 'w', encoding=encoding, errors='ignore') as f:
                    f.write(response.text)
            else:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
            self.total_files += 1
            self.downloaded_files += 1
            self.window.after(0, self.update_progress)
            self.log(f"已保存{resource_type}: {file_path}")
            
        except requests.exceptions.RequestException as e:
            self.log(f"下载{resource_type}失败 {url}: {str(e)}", 'error')
        except Exception as e:
            self.log(f"保存{resource_type}失败 {url}: {str(e)}", 'error')
            
    def get_extension_from_content_type(self, content_type, url):
        # 从Content-Type获取扩展名
        if 'javascript' in content_type:
            return '.js'
        elif 'css' in content_type:
            return '.css'
        elif 'html' in content_type:
            return '.html'
        elif 'image/jpeg' in content_type:
            return '.jpg'
        elif 'image/png' in content_type:
            return '.png'
        elif 'image/gif' in content_type:
            return '.gif'
        elif 'image/webp' in content_type:
            return '.webp'
        elif 'image/svg+xml' in content_type:
            return '.svg'
        
        # 从URL获取扩展名
        ext = os.path.splitext(url)[1]
        if ext:
            return ext
            
        # 默认扩展名
        if 'image' in content_type:
            return '.jpg'
        return '.bin'
        
    def is_same_domain(self, url1, url2):
        return urllib.parse.urlparse(url1).netloc == urllib.parse.urlparse(url2).netloc
        
    def crawling_complete(self):
        self.is_crawling = False
        self.progress['value'] = 100
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="爬取完成！")
        self.log("爬取完成！")
        messagebox.showinfo("完成", "网站爬取完成！")
        
    def crawling_stopped(self):
        self.is_crawling = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="爬取已停止")
        self.log("爬取已停止", 'error')
        messagebox.showinfo("已停止", "网站爬取已停止！")
        
    def show_help(self, title, message):
        """显示帮助信息"""
        help_window = tk.Toplevel(self.window)
        help_window.title(f"{title} - 帮助")
        help_window.geometry("400x200")
        help_window.transient(self.window)
        help_window.grab_set()
        
        # 帮助内容
        help_frame = ttk.Frame(help_window, padding="20")
        help_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(help_frame, text=title, style="Header.TLabel").grid(row=0, column=0, pady=(0, 10))
        
        help_text = scrolledtext.ScrolledText(help_frame, width=40, height=8, wrap=tk.WORD)
        help_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        help_text.insert(tk.END, message)
        help_text.config(state='disabled')
        
        ttk.Button(help_frame, text="关闭", command=help_window.destroy).grid(row=2, column=0, pady=10)
        
        help_window.columnconfigure(0, weight=1)
        help_window.rowconfigure(0, weight=1)
        help_frame.columnconfigure(0, weight=1)
        help_frame.rowconfigure(1, weight=1)
        
    def show_general_help(self):
        """显示一般帮助信息"""
        help_window = tk.Toplevel(self.window)
        help_window.title("使用帮助")
        help_window.geometry("600x500")
        help_window.transient(self.window)
        help_window.grab_set()
        
        # 帮助内容
        help_frame = ttk.Frame(help_window, padding="20")
        help_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(help_frame, text="网站爬虫工具使用帮助", style="Header.TLabel").grid(row=0, column=0, pady=(0, 10))
        
        help_text = scrolledtext.ScrolledText(help_frame, width=60, height=25, wrap=tk.WORD)
        help_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        help_content = """
网站爬虫工具使用指南

1. 基本设置
   - 目标网站URL：输入要爬取的网站地址，必须以http://或https://开头
   - 保存路径：选择下载文件的保存位置，默认为程序所在目录下的downloaded_sites文件夹

2. 爬取选项
   - 爬取深度：决定爬虫递归爬取的层数，1表示只爬取当前页面
   - 默认编码：网页的编码方式，如果网页显示乱码，可以尝试切换不同的编码
   - 爬取模式：
     * 单页爬取：只爬取当前页面及其资源
     * 整站爬取：爬取整个网站的所有页面和资源
     * 仅爬取图片：只下载网站中的图片资源

3. 下载选项
   - HTML：是否下载网页的HTML文件
   - CSS：是否下载样式表文件
   - JS：是否下载JavaScript脚本文件
   - 图片：是否下载网站中的图片资源

4. 高级选项
   - 请求延迟：每次请求之间的延迟时间，单位为秒，增加延迟可以减轻对目标服务器的压力
   - 超时设置：请求超时时间，单位为秒，如果请求超过此时间没有响应，将视为失败

5. 使用技巧
   - 爬取大型网站时，建议先使用"单页爬取"模式测试
   - 如果遇到下载失败，可以尝试增加超时时间或请求延迟
   - 爬取图片时，建议同时下载CSS和JS，以确保获取所有图片资源
   - 使用"仅爬取图片"模式时，程序会自动禁用HTML下载，启用CSS、JS和图片下载

6. 注意事项
   - 请遵守网站的robots.txt规则和使用条款
   - 不要对同一网站进行过于频繁的爬取，以免对服务器造成压力
   - 下载的内容仅供个人学习使用，请勿用于商业用途
   - 部分网站可能有反爬虫机制，可能需要调整爬取策略

7. 版权归属
   - 软件由OE源码网开发
   - OE源码网www.2oe.cn
   - 一家更新精品资源的网站
"""
        help_text.insert(tk.END, help_content)
        help_text.config(state='disabled')
        
        ttk.Button(help_frame, text="关闭", command=help_window.destroy).grid(row=2, column=0, pady=10)
        
        help_window.columnconfigure(0, weight=1)
        help_window.rowconfigure(0, weight=1)
        help_frame.columnconfigure(0, weight=1)
        help_frame.rowconfigure(1, weight=1)
        
    def on_closing(self):
        """窗口关闭事件处理"""
        if self.is_crawling:
            if messagebox.askyesno("确认", "爬取正在进行中，确定要退出吗？"):
                self.should_stop = True
                self.window.after(1000, self.window.destroy)
        else:
            self.window.destroy()
        
    def show_error(self, error_message):
        self.is_crawling = False
        self.progress.stop()
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="爬取失败")
        self.log(f"爬取失败: {error_message}", 'error')
        messagebox.showerror("错误", f"爬取过程中出现错误：{error_message}")
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    crawler = WebsiteCrawler()
    crawler.run() 