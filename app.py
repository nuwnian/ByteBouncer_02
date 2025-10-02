import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import psutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import threading
import hashlib
import shutil
from send2trash import send2trash
import subprocess
import json
import sys
import ctypes

# Configuration constants
LARGE_FILE_THRESHOLD = 100 * 1024 * 1024  # 100MB
MAX_FILES_DISPLAY = 200
MAX_LARGE_FILES_DISPLAY = 50
DUPLICATE_THRESHOLD = 1024  # Minimum file size to check for duplicates (1KB)
CONFIG_FILE = "bytebouncer_config.json"

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ByteBouncerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set window title with admin status
        admin_title = " [🛡️ ADMINISTRATOR]" if self.is_admin() else ""
        self.title(f"ByteBouncer - Disk Space Analyzer{admin_title}")
        self.geometry("1200x700")
        
        self.scan_results = None
        self.duplicate_results = None
        self.is_scanning = False
        self.selected_files = set()
        
        self.load_config()
        self.create_ui()
        self.load_drives()
        
        # Set up close handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_ui(self):
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)
        
        # Logo
        self.logo = ctk.CTkLabel(self.sidebar, text="💾 ByteBouncer", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        self.logo.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Drives section
        ctk.CTkLabel(self.sidebar, text="Available Drives:", 
                    font=ctk.CTkFont(size=14, weight="bold")).grid(row=1, column=0, padx=20, pady=(10, 5))
        
        self.drives_frame = ctk.CTkFrame(self.sidebar)
        self.drives_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        # Scan options
        ctk.CTkLabel(self.sidebar, text="Scan Options:", 
                    font=ctk.CTkFont(size=14, weight="bold")).grid(row=3, column=0, padx=20, pady=(20, 5))
        
        self.path_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Path to scan")
        self.path_entry.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        self.path_entry.insert(0, os.path.expanduser("~"))
        
        self.browse_btn = ctk.CTkButton(self.sidebar, text="Browse", command=self.browse_folder)
        self.browse_btn.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.sidebar, text="Scan Depth:").grid(row=6, column=0, padx=20, pady=(10, 0))
        self.depth_slider = ctk.CTkSlider(self.sidebar, from_=1, to=5, number_of_steps=4)
        self.depth_slider.set(3)
        self.depth_slider.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        
        self.depth_label = ctk.CTkLabel(self.sidebar, text="3 levels")
        self.depth_label.grid(row=8, column=0, padx=20, pady=0)
        self.depth_slider.configure(command=self.update_depth_label)
        
        # Scan button
        self.scan_btn = ctk.CTkButton(self.sidebar, text="🔍 Start Scan", 
                                      command=self.start_scan, height=40,
                                      font=ctk.CTkFont(size=14, weight="bold"))
        self.scan_btn.grid(row=9, column=0, padx=20, pady=20, sticky="ew")
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self.sidebar)
        self.progress.grid(row=10, column=0, padx=20, pady=5, sticky="ew")
        self.progress.set(0)
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Tabview
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.tabview.add("Overview")
        self.tabview.add("Categories")
        self.tabview.add("File Browser")
        self.tabview.add("Duplicates")
        self.tabview.add("Cleanup")
        
        self.setup_overview_tab()
        self.setup_categories_tab()
        self.setup_browser_tab()
        self.setup_duplicates_tab()
        self.setup_cleanup_tab()
        
        # Status bar
        self.status_label = ctk.CTkLabel(self, text="Ready to scan", anchor="w")
        self.status_label.grid(row=1, column=1, sticky="ew", padx=20, pady=(0, 10))
    
    def setup_overview_tab(self):
        tab = self.tabview.tab("Overview")
        
        # Metrics frame
        metrics = ctk.CTkFrame(tab)
        metrics.pack(fill="x", padx=10, pady=10)
        
        self.metric_files = self.create_metric(metrics, "Total Files", "0", 0)
        self.metric_size = self.create_metric(metrics, "Total Size", "0 B", 1)
        self.metric_large = self.create_metric(metrics, "Large Files", "0", 2)
        self.metric_cats = self.create_metric(metrics, "Categories", "0", 3)
        
        # Info text
        self.overview_text = ctk.CTkTextbox(tab, wrap="word")
        self.overview_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.overview_text.insert("1.0", "📊 Scan a folder to see analysis results\n\n"
                                         "ByteBouncer will categorize your files and help you:\n"
                                         "• Identify large files taking up space\n"
                                         "• See file distribution by type\n"
                                         "• Find cleanup opportunities\n"
                                         "• Manage your disk space efficiently")
        self.overview_text.configure(state="disabled")
    
    def setup_categories_tab(self):
        tab = self.tabview.tab("Categories")
        
        # Treeview for categories
        columns = ("Category", "Files", "Size")
        self.cat_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.cat_tree.heading(col, text=col)
            self.cat_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.cat_tree.yview)
        self.cat_tree.configure(yscrollcommand=scrollbar.set)
        
        self.cat_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
    
    def setup_browser_tab(self):
        tab = self.tabview.tab("File Browser")
        
        # Admin warning banner (if running as admin)
        if self.is_admin():
            admin_banner = ctk.CTkFrame(tab, fg_color=("#FFE4E1", "#8B0000"), corner_radius=10)
            admin_banner.pack(fill="x", padx=10, pady=(10, 5))
            
            banner_label = ctk.CTkLabel(
                admin_banner,
                text="🚨 ADMINISTRATOR MODE - Use with caution! Can delete system files 🚨",
                text_color=("#8B0000", "#FFE4E1"),
                font=ctk.CTkFont(size=14, weight="bold")
            )
            banner_label.pack(pady=8)
        
        # Quick filter options (simplified)
        filter_frame = ctk.CTkFrame(tab)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        # Quick sort/view options
        ctk.CTkLabel(filter_frame, text="Quick Actions:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkButton(filter_frame, text="🟢 Show Safe Only", command=lambda: self.quick_filter('safe'), width=120).pack(side="left", padx=2)
        ctk.CTkButton(filter_frame, text="🟡 Show Large Only", command=lambda: self.quick_filter('large'), width=120).pack(side="left", padx=2)
        ctk.CTkButton(filter_frame, text="📊 Show All", command=lambda: self.quick_filter('all'), width=100).pack(side="left", padx=2)
        
        # File operations frame
        ops_frame = ctk.CTkFrame(tab)
        ops_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(ops_frame, text="🗑️ Delete Selected", command=self.delete_selected_files).pack(side="left", padx=5)
        ctk.CTkButton(ops_frame, text="📂 Open Location", command=self.open_file_location).pack(side="left", padx=5)
        ctk.CTkButton(ops_frame, text="🔍 Check Selected", command=self.check_selected_files).pack(side="left", padx=5)
        ctk.CTkButton(ops_frame, text="🐛 Debug Paths", command=self.debug_file_paths).pack(side="left", padx=5)
        
        # Admin status and button with prominent badge
        admin_frame = ctk.CTkFrame(ops_frame)
        admin_frame.pack(side="right", padx=5)
        
        if self.is_admin():
            # Prominent admin badge with red background
            admin_badge = ctk.CTkLabel(
                admin_frame, 
                text="🛡️ ADMINISTRATOR",
                fg_color=("#DC143C", "#8B0000"),  # Red background (light, dark)
                text_color=("white", "white"),
                corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            admin_badge.pack(side="left", padx=2, pady=2)
            
            # Warning label
            warning_label = ctk.CTkLabel(
                admin_frame,
                text="⚠️ Can delete system files",
                text_color=("#FF6B35", "#FF8C42"),
                font=ctk.CTkFont(size=10)
            )
            warning_label.pack(side="left", padx=2)
        else:
            # Regular user badge
            user_badge = ctk.CTkLabel(
                admin_frame,
                text="👤 USER MODE",
                fg_color=("#4A90E2", "#2E5B8C"),  # Blue background
                text_color=("white", "white"),
                corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            user_badge.pack(side="left", padx=2, pady=2)
            
            # Run as admin button
            ctk.CTkButton(admin_frame, text="🔓 Run as Admin", command=self.restart_as_admin, width=120).pack(side="left", padx=2)
        
        self.selection_label = ctk.CTkLabel(ops_frame, text="Selected: 0 files")
        self.selection_label.pack(side="right", padx=5)
        
        # File list frame
        list_frame = ctk.CTkFrame(tab)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("✓", "Safety", "Name", "Size", "Category", "Modified", "Path")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        widths = [30, 60, 160, 100, 100, 150, 300]
        for col, width in zip(columns, widths):
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=width)
        
        # Configure tags for color coding
        self.file_tree.tag_configure('safe', background='#E8F5E8')  # Light green
        self.file_tree.tag_configure('caution', background='#FFF4E6')  # Light orange  
        self.file_tree.tag_configure('danger', background='#FFE4E4')  # Light red
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind events and disable default treeview behavior
        self.file_tree.bind("<Button-1>", self.on_file_click)
        self.file_tree.bind("<Double-1>", self.on_file_double_click)
        self.file_tree.bind("<Button-3>", self.show_context_menu)  # Right-click
        
        # Disable default treeview selection behavior that might cause file opening
        self.file_tree.bind("<<TreeviewSelect>>", lambda e: None)
        
        # Create context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="📂 Open Location", command=self.open_file_location)
        self.context_menu.add_command(label="🔍 Check File", command=self.check_single_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="✓ Select", command=self.select_current_file)
        self.context_menu.add_command(label="❌ Deselect", command=self.deselect_current_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Delete", command=self.delete_current_file)
    
    def setup_duplicates_tab(self):
        tab = self.tabview.tab("Duplicates")
        
        # Control frame
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(control_frame, text="🔍 Find Duplicates", 
                     command=self.start_duplicate_scan).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="🗑️ Delete Selected", 
                     command=self.delete_selected_duplicates).pack(side="left", padx=5)
        
        self.dup_progress = ctk.CTkProgressBar(control_frame)
        self.dup_progress.pack(side="right", padx=5, fill="x", expand=True)
        self.dup_progress.set(0)
        
        # Duplicates list
        columns = ("✓", "Name", "Size", "Count", "Total Waste", "Paths")
        self.dup_tree = ttk.Treeview(tab, columns=columns, show="headings", height=20)
        
        widths = [30, 200, 100, 60, 120, 400]
        for col, width in zip(columns, widths):
            self.dup_tree.heading(col, text=col)
            self.dup_tree.column(col, width=width)
        
        dup_scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.dup_tree.yview)
        self.dup_tree.configure(yscrollcommand=dup_scrollbar.set)
        
        self.dup_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        dup_scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        self.dup_tree.bind("<Button-1>", self.on_duplicate_click)
    
    def setup_cleanup_tab(self):
        tab = self.tabview.tab("Cleanup")
        
        # Large files section
        ctk.CTkLabel(tab, text="🔴 Large Files (>100MB)", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(padx=10, pady=(10, 5), anchor="w")
        
        # Cleanup operations frame
        cleanup_ops = ctk.CTkFrame(tab)
        cleanup_ops.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(cleanup_ops, text="🗑️ Delete Selected", 
                     command=self.delete_large_files).pack(side="left", padx=5)
        ctk.CTkButton(cleanup_ops, text="📊 Analyze Space Savings", 
                     command=self.analyze_cleanup).pack(side="left", padx=5)
        
        columns = ("✓", "Name", "Size", "Path")
        self.cleanup_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        
        widths = [30, 200, 100, 400]
        for col, width in zip(columns, widths):
            self.cleanup_tree.heading(col, text=col)
            self.cleanup_tree.column(col, width=width)
        
        cleanup_scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.cleanup_tree.yview)
        self.cleanup_tree.configure(yscrollcommand=cleanup_scrollbar.set)
        
        self.cleanup_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        cleanup_scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        self.cleanup_tree.bind("<Button-1>", self.on_cleanup_click)
    
    def create_metric(self, parent, title, value, column):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=column, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)
        
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=12)).pack(pady=(10, 0))
        label = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=(0, 10))
        return label
    
    def load_drives(self):
        for widget in self.drives_frame.winfo_children():
            widget.destroy()
        
        row = 0
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                frame = ctk.CTkFrame(self.drives_frame)
                frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
                
                ctk.CTkLabel(frame, text=f"{partition.device}", 
                            font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5, 0))
                
                progress = ctk.CTkProgressBar(frame)
                progress.pack(fill="x", padx=5, pady=5)
                progress.set(usage.percent / 100)
                
                size_text = f"{self.format_size(usage.used)} / {self.format_size(usage.total)}"
                ctk.CTkLabel(frame, text=size_text, font=ctk.CTkFont(size=10)).pack(padx=5, pady=(0, 5))
                
                row += 1
            except:
                continue
    
    def update_depth_label(self, value):
        self.depth_label.configure(text=f"{int(value)} levels")
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)
    
    def start_scan(self):
        if self.is_scanning:
            messagebox.showwarning("Scan in Progress", "A scan is already running!")
            return
        
        path = self.path_entry.get()
        if not os.path.exists(path):
            messagebox.showerror("Error", "Path does not exist!")
            return
        
        self.is_scanning = True
        self.scan_btn.configure(state="disabled", text="Scanning...")
        self.progress.set(0)
        self.progress.start()
        
        depth = int(self.depth_slider.get())
        
        thread = threading.Thread(target=self.scan_thread, args=(path, depth))
        thread.daemon = True
        thread.start()
    
    def scan_thread(self, path, depth):
        try:
            results = self.scan_directory(path, depth)
            self.after(0, self.scan_complete, results)
        except Exception as e:
            self.after(0, self.scan_error, str(e))
    
    def scan_directory(self, path, max_depth=3, current_depth=0):
        results = {
            'files': [],
            'categories': defaultdict(lambda: {'count': 0, 'size': 0}),
            'large_files': [],
            'file_hashes': {}  # For duplicate detection
        }
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        if not os.access(path, os.R_OK):
            raise PermissionError(f"No read permission for: {path}")
        
        category_map = {
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx', '.rtf', '.odt'],
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff', '.ico'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
            'Executables': ['.exe', '.msi', '.dll', '.bat', '.cmd', '.com'],
            'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.json', '.xml', '.cs', '.php'],
            'System': ['.sys', '.ini', '.log', '.tmp', '.cache'],
            'Fonts': ['.ttf', '.otf', '.woff', '.woff2']
        }
        
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    try:
                        if entry.is_file():
                            stat = entry.stat()
                            size = stat.st_size
                            ext = Path(entry.name).suffix.lower()
                            
                            category = 'Other'
                            for cat, extensions in category_map.items():
                                if ext in extensions:
                                    category = cat
                                    break
                            
                            results['categories'][category]['count'] += 1
                            results['categories'][category]['size'] += size
                            
                            file_info = {
                                'path': os.path.normpath(entry.path),  # Normalize path for Windows
                                'name': entry.name,
                                'size': size,
                                'modified': datetime.fromtimestamp(stat.st_mtime),
                                'category': category
                            }
                            results['files'].append(file_info)
                            
                            if size > LARGE_FILE_THRESHOLD:
                                results['large_files'].append(file_info)
                        
                        elif entry.is_dir() and current_depth < max_depth:
                            subdir_results = self.scan_directory(entry.path, max_depth, current_depth + 1)
                            results['files'].extend(subdir_results['files'])
                            for cat, data in subdir_results['categories'].items():
                                results['categories'][cat]['count'] += data['count']
                                results['categories'][cat]['size'] += data['size']
                            results['large_files'].extend(subdir_results['large_files'])
                    
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass
        
        return results
    
    def scan_complete(self, results):
        self.scan_results = results
        self.is_scanning = False
        self.scan_btn.configure(state="normal", text="🔍 Start Scan")
        self.progress.stop()
        self.progress.set(1)
        
        self.update_ui_with_results()
        self.status_label.configure(text=f"Scan complete! Found {len(results['files']):,} files")
        messagebox.showinfo("Success", f"Scan complete!\nFound {len(results['files']):,} files")
    
    def scan_error(self, error):
        self.is_scanning = False
        self.scan_btn.configure(state="normal", text="🔍 Start Scan")
        self.progress.stop()
        self.progress.set(0)
        messagebox.showerror("Scan Error", f"Error during scan: {error}")
    
    def update_ui_with_results(self):
        if not self.scan_results:
            return
        
        results = self.scan_results
        total_files = len(results['files'])
        total_size = sum(f['size'] for f in results['files'])
        
        # Update metrics
        self.metric_files.configure(text=f"{total_files:,}")
        self.metric_size.configure(text=self.format_size(total_size))
        self.metric_large.configure(text=f"{len(results['large_files']):,}")
        self.metric_cats.configure(text=f"{len(results['categories'])}")
        
        # Update overview
        self.overview_text.configure(state="normal")
        self.overview_text.delete("1.0", "end")
        overview = f"📊 Scan Results\n\n"
        overview += f"Total Files: {total_files:,}\n"
        overview += f"Total Size: {self.format_size(total_size)}\n"
        overview += f"Large Files: {len(results['large_files']):,}\n\n"
        overview += "Top Categories:\n"
        for cat, data in sorted(results['categories'].items(), key=lambda x: x[1]['size'], reverse=True)[:5]:
            overview += f"  • {cat}: {data['count']:,} files ({self.format_size(data['size'])})\n"
        self.overview_text.insert("1.0", overview)
        self.overview_text.configure(state="disabled")
        
        # Update categories
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)
        
        for cat, data in sorted(results['categories'].items(), key=lambda x: x[1]['size'], reverse=True):
            self.cat_tree.insert("", "end", values=(cat, f"{data['count']:,}", self.format_size(data['size'])))
        
        # Update file browser
        self.populate_file_browser(results['files'])
        
        # Update cleanup
        for item in self.cleanup_tree.get_children():
            self.cleanup_tree.delete(item)
        
        for f in sorted(results['large_files'], key=lambda x: x['size'], reverse=True)[:MAX_LARGE_FILES_DISPLAY]:
            self.cleanup_tree.insert("", "end", values=("", f['name'], self.format_size(f['size']), f['path']))
        
        # Filter options removed - now using visual color coding
    
    def populate_file_browser(self, files):
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        for f in sorted(files, key=lambda x: x['size'], reverse=True)[:MAX_FILES_DISPLAY]:
            # Determine safety level and color
            is_important, reason = self.is_important_file(f['path'])
            file_size_mb = f['size'] / (1024 * 1024)
            
            if is_important:
                safety_icon = "🔴"
                safety_tag = 'danger'
            elif file_size_mb > 100:
                safety_icon = "🟡"
                safety_tag = 'caution'
            else:
                safety_icon = "🟢"
                safety_tag = 'safe'
            
            item = self.file_tree.insert("", "end", values=(
                "",  # Checkbox column
                safety_icon,  # Safety indicator
                f['name'],
                self.format_size(f['size']),
                f['category'],
                f['modified'].strftime('%Y-%m-%d %H:%M'),
                f['path']
            ), tags=(safety_tag,))
    
    def quick_filter(self, filter_type):
        """Quick filter based on visual safety indicators"""
        if not self.scan_results:
            return
        
        all_files = self.scan_results['files']
        
        if filter_type == 'safe':
            # Show only files that would be marked as safe (green)
            filtered = []
            for f in all_files:
                is_important, _ = self.is_important_file(f['path'])
                file_size_mb = f['size'] / (1024 * 1024)
                if not is_important and file_size_mb <= 100:
                    filtered.append(f)
        elif filter_type == 'large':
            # Show only large files (orange/yellow)  
            filtered = [f for f in all_files if f['size'] >= 100 * 1024 * 1024]  # >100MB
        else:  # 'all'
            filtered = all_files
        
        self.populate_file_browser(filtered)
        
        # Update button text to show active filter
        messagebox.showinfo("Filter Applied", 
                          f"Showing {len(filtered)} files\n"
                          f"Filter: {filter_type.title()} files")
    
    @staticmethod
    def format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    @staticmethod
    def is_admin():
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    @staticmethod
    def run_as_admin():
        """Restart the application with administrator privileges"""
        try:
            if ByteBouncerApp.is_admin():
                return True
            else:
                # Re-run the program with admin privileges
                script_path = os.path.abspath(__file__)
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, f'"{script_path}"', None, 1
                )
                return False
        except Exception as e:
            messagebox.showerror("Admin Error", f"Could not run as administrator: {e}")
            return False
    
    def load_config(self):
        """Load application configuration"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    'last_scan_path': os.path.expanduser("~"),
                    'scan_depth': 3,
                    'theme': 'dark'
                }
        except Exception:
            self.config = {
                'last_scan_path': os.path.expanduser("~"),
                'scan_depth': 3,
                'theme': 'dark'
            }
    
    def save_config(self):
        """Save application configuration"""
        try:
            self.config['last_scan_path'] = self.path_entry.get()
            self.config['scan_depth'] = int(self.depth_slider.get())
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass
    
    def calculate_file_hash(self, filepath, chunk_size=8192):
        """Calculate MD5 hash of file for duplicate detection"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, OSError):
            return None
    
    def find_duplicates(self, files):
        """Find duplicate files based on size and hash"""
        duplicates = defaultdict(list)
        
        # Group by size first (faster)
        size_groups = defaultdict(list)
        for file_info in files:
            if file_info['size'] >= DUPLICATE_THRESHOLD:
                size_groups[file_info['size']].append(file_info)
        
        # Check hash for files with same size
        for size, file_list in size_groups.items():
            if len(file_list) > 1:
                hash_groups = defaultdict(list)
                for file_info in file_list:
                    file_hash = self.calculate_file_hash(file_info['path'])
                    if file_hash:
                        hash_groups[file_hash].append(file_info)
                
                for file_hash, dup_files in hash_groups.items():
                    if len(dup_files) > 1:
                        duplicates[file_hash] = dup_files
        
        return duplicates
    
    def start_duplicate_scan(self):
        """Start duplicate file detection"""
        if not self.scan_results:
            messagebox.showwarning("No Scan Data", "Please scan a directory first!")
            return
        
        if self.is_scanning:
            messagebox.showwarning("Scan in Progress", "Please wait for current scan to complete!")
            return
        
        self.is_scanning = True
        self.dup_progress.start()
        
        thread = threading.Thread(target=self.duplicate_scan_thread)
        thread.daemon = True
        thread.start()
    
    def duplicate_scan_thread(self):
        """Background thread for duplicate detection"""
        try:
            duplicates = self.find_duplicates(self.scan_results['files'])
            self.after(0, self.duplicate_scan_complete, duplicates)
        except Exception as e:
            self.after(0, self.duplicate_scan_error, str(e))
    
    def duplicate_scan_complete(self, duplicates):
        """Handle completion of duplicate scan"""
        self.duplicate_results = duplicates
        self.is_scanning = False
        self.dup_progress.stop()
        self.dup_progress.set(1)
        
        # Clear existing items
        for item in self.dup_tree.get_children():
            self.dup_tree.delete(item)
        
        # Populate duplicate results
        for file_hash, dup_files in duplicates.items():
            if len(dup_files) > 1:
                total_size = dup_files[0]['size']
                waste_size = total_size * (len(dup_files) - 1)
                paths = "; ".join([f['path'] for f in dup_files])
                
                self.dup_tree.insert("", "end", values=(
                    "",
                    dup_files[0]['name'],
                    self.format_size(total_size),
                    len(dup_files),
                    self.format_size(waste_size),
                    paths
                ))
        
        count = len(duplicates)
        messagebox.showinfo("Duplicates Found", f"Found {count} sets of duplicate files!")
    
    def duplicate_scan_error(self, error):
        """Handle duplicate scan error"""
        self.is_scanning = False
        self.dup_progress.stop()
        self.dup_progress.set(0)
        messagebox.showerror("Duplicate Scan Error", f"Error during duplicate scan: {error}")
    
    def on_file_click(self, event):
        """Handle file tree click for selection (checkbox toggle)"""
        item = self.file_tree.identify_row(event.y)
        if item:
            # Toggle checkbox regardless of click position for now
            current_value = self.file_tree.item(item)['values'][0]
            new_value = "✓" if current_value != "✓" else ""
            values = list(self.file_tree.item(item)['values'])
            values[0] = new_value
            self.file_tree.item(item, values=values)
            
            file_path = values[6]  # Path is now at index 6 (added safety column)
            if new_value == "✓":
                self.selected_files.add(file_path)
            else:
                self.selected_files.discard(file_path)
            
            # Update selection counter
            self.update_selection_counter()
        
        # Prevent default treeview behavior
        return "break"
    
    def on_file_double_click(self, event):
        """Handle double-click to open file location"""
        self.open_file_location()
    
    def on_duplicate_click(self, event):
        """Handle duplicate tree click"""
        item = self.dup_tree.identify_row(event.y)
        if item:
            current_value = self.dup_tree.item(item)['values'][0]
            new_value = "✓" if current_value != "✓" else ""
            values = list(self.dup_tree.item(item)['values'])
            values[0] = new_value
            self.dup_tree.item(item, values=values)
    
    def on_cleanup_click(self, event):
        """Handle cleanup tree click"""
        item = self.cleanup_tree.identify_row(event.y)
        if item:
            current_value = self.cleanup_tree.item(item)['values'][0]
            new_value = "✓" if current_value != "✓" else ""
            values = list(self.cleanup_tree.item(item)['values'])
            values[0] = new_value
            self.cleanup_tree.item(item, values=values)
    
    def is_important_file(self, file_path):
        """Check if a file might be important and shouldn't be deleted carelessly"""
        file_ext = Path(file_path).suffix.lower()
        file_path_lower = file_path.lower()
        
        # Only flag truly critical system locations
        critical_locations = [
            'windows\\system32', 'windows\\syswow64', 'windows\\winsxs'
        ]
        
        # Only flag if in critical system directories
        for location in critical_locations:
            if location in file_path_lower:
                return True, f"Critical system directory"
        
        # Flag system files only in critical locations
        if file_ext in ['.sys', '.dll'] and any(loc in file_path_lower for loc in critical_locations):
            return True, f"Critical system file"
        
        # Flag important config/database files
        if file_ext in ['.ini', '.cfg', '.conf', '.config'] and 'windows' in file_path_lower:
            return True, f"System configuration"
        
        if file_ext in ['.db', '.sqlite'] and 'appdata' not in file_path_lower:
            return True, f"Database file"
        
        # Flag project files
        if file_ext in ['.sln', '.proj', '.csproj', '.vcxproj']:
            return True, f"Project file"
        
        return False, ""
    
    def analyze_file_safety(self, files):
        """Analyze selected files for safety warnings"""
        warnings = []
        categories = {'safe': 0, 'caution': 0, 'dangerous': 0}
        
        for file_path in files:
            is_important, reason = self.is_important_file(file_path)
            file_size = 0
            try:
                file_size = os.path.getsize(file_path) / (1024*1024)  # MB
            except:
                pass
            
            if is_important:
                categories['dangerous'] += 1
                warnings.append(f"⚠️ {os.path.basename(file_path)} - {reason}")
            elif file_size > 100:  # Files > 100MB
                categories['caution'] += 1
                warnings.append(f"📦 {os.path.basename(file_path)} - Large file ({file_size:.1f} MB)")
            else:
                categories['safe'] += 1
        
        return warnings, categories
    
    def show_success_notification(self, successful_deletes, total_size_mb, categories):
        """Show detailed success notification"""
        # Calculate space freed
        if total_size_mb >= 1024:
            size_str = f"{total_size_mb/1024:.2f} GB"
        else:
            size_str = f"{total_size_mb:.1f} MB"
        
        success_msg = f"🎉 Deletion Successful!\n\n"
        success_msg += f"✅ Files deleted: {successful_deletes}\n"
        success_msg += f"💾 Space freed: {size_str}\n\n"
        
        if categories['safe'] > 0:
            success_msg += f"🟢 Safe files: {categories['safe']}\n"
        if categories['caution'] > 0:
            success_msg += f"🟡 Large files: {categories['caution']}\n"
        if categories['dangerous'] > 0:
            success_msg += f"🔴 System files: {categories['dangerous']}\n"
        
        success_msg += f"\n📁 All files moved to Recycle Bin - you can restore them if needed!"
        
        messagebox.showinfo("Success", success_msg)
    
    def delete_selected_files(self):
        """Delete selected files safely using send2trash with enhanced error handling and safety warnings"""
        if not self.selected_files:
            messagebox.showwarning("No Selection", "Please select files to delete!")
            return
        
        # Analyze file safety first
        warnings, categories = self.analyze_file_safety(self.selected_files)
        
        # Create confirmation message with safety analysis
        count = len(self.selected_files)
        confirm_msg = f"Delete {count} selected files?\n\n"
        
        if categories['safe'] > 0:
            confirm_msg += f"🟢 Safe to delete: {categories['safe']} files\n"
        if categories['caution'] > 0:
            confirm_msg += f"🟡 Large files: {categories['caution']} files\n"
        if categories['dangerous'] > 0:
            confirm_msg += f"🔴 Important files: {categories['dangerous']} files\n"
        
        confirm_msg += f"\n📁 Files will be moved to Recycle Bin (recoverable).\n"
        
        # Show warnings if any dangerous files
        if warnings:
            confirm_msg += f"\n⚠️ WARNINGS:\n"
            for warning in warnings[:5]:  # Show first 5 warnings
                confirm_msg += f"  {warning}\n"
            if len(warnings) > 5:
                confirm_msg += f"  ... and {len(warnings) - 5} more warnings\n"
            
            # Extra confirmation for dangerous files
            if categories['dangerous'] > 0:
                confirm_msg += f"\n🚨 CAUTION: Some files may be important system files!\n"
                if not messagebox.askyesno("⚠️ Confirm Risky Deletion", confirm_msg):
                    return
            elif not messagebox.askyesno("Confirm Deletion", confirm_msg):
                return
        else:
            if not messagebox.askyesno("Confirm Deletion", confirm_msg):
                return
        
        successful_deletes = 0
        failed_files = []
        permission_errors = []
        not_found_errors = []
        locked_files = []
        total_size_deleted = 0  # Track total size deleted
        deleted_file_info = []  # Track what was deleted for success notification
        
        for file_path in self.selected_files:
            try:
                # Normalize the path to handle any path format issues
                normalized_path = os.path.normpath(file_path)
                
                if not os.path.exists(normalized_path):
                    not_found_errors.append(file_path)
                    continue
                
                # Check if file is in use or locked
                try:
                    with open(normalized_path, 'r+b'):
                        pass
                except (PermissionError, OSError) as e:
                    if "being used by another process" in str(e).lower():
                        locked_files.append(file_path)
                        continue
                    elif "access is denied" in str(e).lower():
                        # This might need admin privileges
                        permission_errors.append(f"{os.path.basename(file_path)}: Permission denied")
                        continue
                
                # Get file size before deletion
                try:
                    file_size = os.path.getsize(normalized_path)
                    total_size_deleted += file_size
                    deleted_file_info.append({
                        'name': os.path.basename(file_path),
                        'size': file_size,
                        'path': file_path
                    })
                except:
                    pass
                
                # Try to delete with send2trash
                send2trash(normalized_path)
                successful_deletes += 1
                
            except PermissionError as e:
                permission_errors.append(f"{os.path.basename(file_path)}: Permission denied")
            except FileNotFoundError:
                not_found_errors.append(file_path)
            except Exception as e:
                error_type = type(e).__name__
                failed_files.append(f"{os.path.basename(file_path)}: {error_type} - {str(e)}")
        
        # Show detailed results
        result_msg = f"Deletion Results:\n"
        result_msg += f"✅ Successfully deleted: {successful_deletes} files\n"
        
        if permission_errors:
            result_msg += f"🔒 Permission denied: {len(permission_errors)} files\n"
        if locked_files:
            result_msg += f"🔐 Files in use: {len(locked_files)} files\n"
        if not_found_errors:
            result_msg += f"❓ Files not found: {len(not_found_errors)} files\n"
        if failed_files:
            result_msg += f"❌ Other errors: {len(failed_files)} files\n"
        
        if successful_deletes > 0:
            # Show enhanced success notification
            total_size_mb = total_size_deleted / (1024 * 1024)
            _, categories = self.analyze_file_safety([info['path'] for info in deleted_file_info])
            self.show_success_notification(successful_deletes, total_size_mb, categories)
            
            # Also show basic result if there were any issues
            if permission_errors or locked_files or not_found_errors or failed_files:
                messagebox.showinfo("Deletion Complete with Issues", result_msg)
        else:
            # Show detailed error information with admin solution
            detailed_msg = result_msg + "\n\nCommon solutions:\n"
            if permission_errors:
                admin_status = "✅ Already running as Admin" if self.is_admin() else "❌ Not running as Admin"
                detailed_msg += f"• {admin_status}\n"
                if not self.is_admin():
                    detailed_msg += "• Click '🔓 Run as Admin' button to restart with privileges\n"
                else:
                    detailed_msg += "• Some system files cannot be deleted even as Admin\n"
            if locked_files:
                detailed_msg += "• Close programs using these files\n"
            if not_found_errors:
                detailed_msg += "• Files may have been moved or deleted\n"
            
            if len(permission_errors + locked_files + failed_files) > 0:
                detailed_msg += "\nDetailed errors:\n"
                all_errors = permission_errors + [f"{os.path.basename(f)}: File in use" for f in locked_files] + failed_files
                detailed_msg += "\n".join(all_errors[:10])
                if len(all_errors) > 10:
                    detailed_msg += f"\n... and {len(all_errors) - 10} more"
            
            # Add admin restart option for permission errors
            if permission_errors and not self.is_admin():
                if messagebox.askyesno("Permission Denied", 
                                     detailed_msg + "\n\nRestart as Administrator to try again?"):
                    self.restart_as_admin()
                    return
            
            messagebox.showerror("Deletion Issues", detailed_msg)
        
        self.selected_files.clear()
        
        # Refresh the scan if any files were deleted
        if successful_deletes > 0:
            if messagebox.askyesno("Refresh", "Refresh scan results to update the view?"):
                self.start_scan()
    
    def delete_selected_duplicates(self):
        """Delete selected duplicate files"""
        selected_items = []
        for item in self.dup_tree.get_children():
            if self.dup_tree.item(item)['values'][0] == "✓":
                selected_items.append(item)
        
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select duplicate sets to clean!")
            return
        
        if not messagebox.askyesno("Confirm Delete", 
                                  f"Delete duplicates from {len(selected_items)} sets?\n"
                                  "This will keep one copy of each file."):
            return
        
        total_deleted = 0
        for item in selected_items:
            paths_str = self.dup_tree.item(item)['values'][5]
            paths = paths_str.split("; ")
            
            # Keep the first file, delete the rest
            for path in paths[1:]:
                try:
                    if os.path.exists(path):
                        send2trash(path)
                        total_deleted += 1
                except Exception:
                    pass
        
        messagebox.showinfo("Cleanup Complete", f"Moved {total_deleted} duplicate files to Recycle Bin!")
        self.start_duplicate_scan()  # Refresh duplicates
    
    def delete_large_files(self):
        """Delete selected large files"""
        selected_items = []
        for item in self.cleanup_tree.get_children():
            if self.cleanup_tree.item(item)['values'][0] == "✓":
                selected_items.append(item)
        
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select large files to delete!")
            return
        
        if not messagebox.askyesno("Confirm Delete", 
                                  f"Move {len(selected_items)} large files to Recycle Bin?"):
            return
        
        deleted_count = 0
        for item in selected_items:
            file_path = self.cleanup_tree.item(item)['values'][3]
            try:
                if os.path.exists(file_path):
                    send2trash(file_path)
                    deleted_count += 1
            except Exception:
                pass
        
        messagebox.showinfo("Cleanup Complete", f"Moved {deleted_count} files to Recycle Bin!")
        if messagebox.askyesno("Refresh", "Refresh scan results?"):
            self.start_scan()
    
    def open_file_location(self):
        """Open file location in Windows Explorer"""
        selected_item = self.file_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a file!")
            return
        
        file_path = self.file_tree.item(selected_item[0])['values'][6]  # Updated for Safety column
        normalized_path = os.path.normpath(file_path)
        
        try:
            # Check if file exists first
            if not os.path.exists(normalized_path):
                messagebox.showerror("File Not Found", f"File does not exist:\n{normalized_path}")
                return
            
            # Use Windows explorer to select the file
            subprocess.run(['explorer', '/select,', normalized_path], check=True)
        except Exception as e:
            # Fallback: try to open the directory
            try:
                directory = os.path.dirname(normalized_path)
                if os.path.exists(directory):
                    subprocess.run(['explorer', directory], check=True)
                    messagebox.showinfo("Directory Opened", f"Opened directory (file not found):\n{directory}")
                else:
                    messagebox.showerror("Error", f"Could not open file location:\n{str(e)}\n\nPath: {normalized_path}")
            except Exception as e2:
                messagebox.showerror("Error", f"Could not open file location:\n{str(e)}\n\nAlso failed to open directory:\n{str(e2)}")
    
    def analyze_cleanup(self):
        """Analyze potential space savings"""
        if not self.scan_results:
            messagebox.showwarning("No Data", "Please scan a directory first!")
            return
        
        large_files_size = sum(f['size'] for f in self.scan_results['large_files'])
        
        duplicate_waste = 0
        if self.duplicate_results:
            for dup_files in self.duplicate_results.values():
                if len(dup_files) > 1:
                    duplicate_waste += dup_files[0]['size'] * (len(dup_files) - 1)
        
        total_potential = large_files_size + duplicate_waste
        
        analysis = f"Space Analysis Report\n"
        analysis += f"=" * 30 + "\n\n"
        analysis += f"Large Files (>100MB): {self.format_size(large_files_size)}\n"
        analysis += f"Duplicate File Waste: {self.format_size(duplicate_waste)}\n"
        analysis += f"Total Potential Savings: {self.format_size(total_potential)}\n\n"
        analysis += f"Recommendations:\n"
        analysis += f"• Review large files for unnecessary data\n"
        analysis += f"• Remove duplicate files\n"
        analysis += f"• Consider archiving old files\n"
        
        messagebox.showinfo("Cleanup Analysis", analysis)
    
    def update_selection_counter(self):
        """Update the selection counter label"""
        count = len(self.selected_files)
        self.selection_label.configure(text=f"Selected: {count} files")
    
    def debug_file_paths(self):
        """Debug function to check file paths"""
        if not self.selected_files:
            messagebox.showwarning("No Selection", "Please select files to debug!")
            return
        
        debug_info = "File Path Debug Information:\n" + "="*40 + "\n\n"
        
        for i, file_path in enumerate(list(self.selected_files)[:5]):  # Show first 5 files
            debug_info += f"File {i+1}:\n"
            debug_info += f"  Original: {repr(file_path)}\n"
            debug_info += f"  Normalized: {repr(os.path.normpath(file_path))}\n"
            debug_info += f"  Exists (orig): {os.path.exists(file_path)}\n"
            debug_info += f"  Exists (norm): {os.path.exists(os.path.normpath(file_path))}\n"
            debug_info += f"  Is absolute: {os.path.isabs(file_path)}\n"
            debug_info += "\n"
        
        if len(self.selected_files) > 5:
            debug_info += f"... and {len(self.selected_files) - 5} more files\n"
        
        messagebox.showinfo("Path Debug Info", debug_info)
    
    def check_selected_files(self):
        """Check status of selected files before deletion"""
        if not self.selected_files:
            messagebox.showwarning("No Selection", "Please select files to check!")
            return
        
        existing_files = []
        missing_files = []
        locked_files = []
        system_files = []
        large_files = []
        
        for file_path in self.selected_files:
            if not os.path.exists(file_path):
                missing_files.append(os.path.basename(file_path))
                continue
            
            existing_files.append(file_path)
            
            # Check if file is locked/in use
            try:
                with open(file_path, 'r+b'):
                    pass
            except (PermissionError, OSError):
                locked_files.append(os.path.basename(file_path))
            
            # Check if it's a system file
            if any(sys_path in file_path.lower() for sys_path in [
                'windows\\system32', 'windows\\installer', 'program files',
                'windows\\winsxs', 'windows\\servicing'
            ]):
                system_files.append(os.path.basename(file_path))
            
            # Check file size
            try:
                size = os.path.getsize(file_path)
                if size > 100 * 1024 * 1024:  # > 100MB
                    large_files.append(f"{os.path.basename(file_path)} ({self.format_size(size)})")
            except OSError:
                pass
        
        # Create status report
        report = f"File Status Report\n{'='*30}\n\n"
        report += f"📊 Total selected: {len(self.selected_files)} files\n"
        report += f"✅ Files found: {len(existing_files)} files\n"
        
        if missing_files:
            report += f"❓ Missing files: {len(missing_files)} files\n"
        if locked_files:
            report += f"🔐 Locked/in-use files: {len(locked_files)} files\n"
        if system_files:
            report += f"⚠️ System files: {len(system_files)} files\n"
        if large_files:
            report += f"📦 Large files: {len(large_files)} files\n"
        
        report += f"\n💡 Recommendations:\n"
        if system_files:
            report += f"• System files may require administrator privileges\n"
        if locked_files:
            report += f"• Close programs using locked files before deletion\n"
        if large_files:
            report += f"• Large files will free significant space\n"
        if missing_files:
            report += f"• Missing files may have been moved or deleted\n"
        
        if locked_files or system_files:
            report += f"\n⚠️ Files that may cause issues:\n"
            problem_files = locked_files + system_files
            report += "\n".join(f"• {f}" for f in problem_files[:10])
            if len(problem_files) > 10:
                report += f"\n• ... and {len(problem_files) - 10} more"
        
        messagebox.showinfo("File Check Results", report)
    
    def is_safe_to_delete(self, file_path):
        """Check if a file is safe to delete"""
        try:
            # Normalize path to handle format issues
            normalized_path = os.path.normpath(file_path)
            
            # Check if file exists
            if not os.path.exists(normalized_path):
                return False, "File not found"
            
            # Check if it's a critical system file
            critical_paths = [
                'windows\\system32\\kernel32.dll',
                'windows\\system32\\ntdll.dll',
                'windows\\system32\\user32.dll',
                'windows\\system32\\gdi32.dll'
            ]
            
            if any(critical in normalized_path.lower() for critical in critical_paths):
                return False, "Critical system file"
            
            # Check if file is in use
            try:
                with open(normalized_path, 'r+b'):
                    pass
            except (PermissionError, OSError) as e:
                if "being used by another process" in str(e).lower():
                    return False, "File in use"
                elif "access is denied" in str(e).lower():
                    return False, "Permission denied"
            
            return True, "Safe to delete"
            
        except Exception as e:
            return False, f"Error checking file: {str(e)}"
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.file_tree.identify_row(event.y)
        if item:
            self.file_tree.selection_set(item)
            self.current_item = item
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
    
    def check_single_file(self):
        """Check status of currently selected file"""
        if not hasattr(self, 'current_item') or not self.current_item:
            return
        
        values = self.file_tree.item(self.current_item)['values']
        file_path = values[6]  # Path is now at index 6 (added Safety column)
        
        if not os.path.exists(file_path):
            messagebox.showwarning("File Check", f"File not found:\n{file_path}")
            return
        
        try:
            stat = os.stat(file_path)
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            # Check file status
            is_safe, safety_msg = self.is_safe_to_delete(file_path)
            
            report = f"File Information\n{'='*30}\n\n"
            report += f"📁 Name: {os.path.basename(file_path)}\n"
            report += f"📊 Size: {self.format_size(size)}\n"
            report += f"📅 Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += f"📂 Location: {os.path.dirname(file_path)}\n"
            report += f"🛡️ Safety: {safety_msg}\n"
            
            if not is_safe:
                report += f"\n⚠️ Warning: This file may not be safe to delete!"
            else:
                report += f"\n✅ This file appears safe to delete."
            
            messagebox.showinfo("File Information", report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not check file:\n{str(e)}")
    
    def select_current_file(self):
        """Select the current file"""
        if not hasattr(self, 'current_item') or not self.current_item:
            return
        
        values = list(self.file_tree.item(self.current_item)['values'])
        values[0] = "✓"
        self.file_tree.item(self.current_item, values=values)
        self.selected_files.add(values[6])  # Updated for Safety column
        self.update_selection_counter()
    
    def deselect_current_file(self):
        """Deselect the current file"""
        if not hasattr(self, 'current_item') or not self.current_item:
            return
        
        values = list(self.file_tree.item(self.current_item)['values'])
        values[0] = ""
        self.file_tree.item(self.current_item, values=values)
        self.selected_files.discard(values[6])  # Updated for Safety column
        self.update_selection_counter()
    
    def delete_current_file(self):
        """Delete the current file"""
        if not hasattr(self, 'current_item') or not self.current_item:
            return
        
        values = self.file_tree.item(self.current_item)['values']
        file_path = values[6]  # Updated for Safety column
        
        # Check if file is safe to delete
        is_safe, safety_msg = self.is_safe_to_delete(file_path)
        
        confirm_msg = f"Delete this file?\n\n{os.path.basename(file_path)}\n"
        confirm_msg += f"Size: {values[2]}\n"
        confirm_msg += f"Status: {safety_msg}\n\n"
        
        if not is_safe:
            confirm_msg += "⚠️ Warning: This file may cause issues if deleted!"
        
        if messagebox.askyesno("Confirm Delete", confirm_msg):
            try:
                if os.path.exists(file_path):
                    send2trash(file_path)
                    messagebox.showinfo("Success", "File moved to Recycle Bin!")
                    # Refresh scan if needed
                    if messagebox.askyesno("Refresh", "Refresh scan results?"):
                        self.start_scan()
                else:
                    messagebox.showwarning("File Not Found", "File no longer exists.")
            except Exception as e:
                messagebox.showerror("Delete Error", f"Could not delete file:\n{str(e)}")
    
    def restart_as_admin(self):
        """Restart the application with administrator privileges"""
        if self.is_admin():
            messagebox.showinfo("Already Admin", "ByteBouncer is already running with administrator privileges!")
            return
        
        if messagebox.askyesno("Restart as Administrator", 
                              "ByteBouncer will restart with administrator privileges.\n\n"
                              "This allows deletion of system files and protected files.\n"
                              "Continue?"):
            try:
                # Save current state
                self.save_config()
                
                # Get the script path
                script_path = os.path.abspath(__file__)
                
                # Try to restart as admin
                result = ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, f'"{script_path}"', None, 1
                )
                
                if result > 32:  # Success
                    # Close current instance
                    self.destroy()
                else:
                    messagebox.showerror("Admin Error", "Failed to restart as administrator.")
                                   
            except Exception as e:
                messagebox.showerror("Admin Error", f"Could not restart as administrator:\n{e}")
    
    def on_closing(self):
        """Handle application closing"""
        self.save_config()
        self.destroy()

if __name__ == "__main__":
    app = ByteBouncerApp()
    app.mainloop()