
import socket
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class UDPPacketSender:
    def __init__(self, root):
        self.root = root
        self.root.title("UDP数据包发送器")
        self.root.geometry("500x350")
        self.root.resizable(True, True)
        
        # 发送状态
        self.is_sending = False
        self.stop_sending = False
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        ttk.Label(main_frame, text="目标IP地址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ip_entry = ttk.Entry(main_frame, width=30)
        self.ip_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.ip_entry.insert(0, "127.0.0.1")
        ttk.Label(main_frame, text="目标端口:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.port_entry = ttk.Entry(main_frame, width=30)
        self.port_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.port_entry.insert(0, "14160")
        ttk.Label(main_frame, text="数据包数量:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.packet_count_entry = ttk.Entry(main_frame, width=30)
        self.packet_count_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.packet_count_entry.insert(0, "100")
        ttk.Label(main_frame, text="发送间隔(秒):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.interval_entry = ttk.Entry(main_frame, width=30)
        self.interval_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        self.interval_entry.insert(0, "0.01")
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        self.start_button = ttk.Button(button_frame, text="开始发送", command=self.start_sending)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(button_frame, text="停止发送", command=self.stop_sending_process, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.clear_button = ttk.Button(button_frame, text="清空日志", command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        ttk.Label(main_frame, text="发送日志:").grid(row=5, column=0, sticky=tk.W, pady=(10, 0))
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, width=60)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def validate_inputs(self):
        """验证输入参数"""
        try:
            ip = self.ip_entry.get().strip()
            port = int(self.port_entry.get().strip())
            packet_count = int(self.packet_count_entry.get().strip())
            interval = float(self.interval_entry.get().strip())
            
            if not ip:
                messagebox.showerror("错误", "请输入目标IP地址")
                return False
            
            if port < 1 or port > 65535:
                messagebox.showerror("错误", "端口号必须在1-65535之间")
                return False
            
            if packet_count < 1:
                messagebox.showerror("错误", "数据包数量必须大于0")
                return False
            
            if interval < 0:
                messagebox.showerror("错误", "发送间隔不能为负数")
                return False
            
            return True
            
        except ValueError as e:
            messagebox.showerror("错误", f"输入参数格式错误: {e}")
            return False
    
    def start_sending(self):
        """开始发送数据包"""
        if not self.validate_inputs():
            return
        
        if self.is_sending:
            messagebox.showwarning("警告", "发送正在进行中")
            return
        
        self.is_sending = True
        self.stop_sending = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 在新线程中发送数据包
        thread = threading.Thread(target=self.send_udp_packets)
        thread.daemon = True
        thread.start()
    
    def stop_sending_process(self):
        """停止发送过程"""
        self.stop_sending = True
        self.log_message("正在停止发送...")
    
    def send_udp_packets(self):
        """发送UDP数据包的主函数"""
        try:
            target_ip = self.ip_entry.get().strip()
            target_port = int(self.port_entry.get().strip())
            packet_count = int(self.packet_count_entry.get().strip())
            interval = float(self.interval_entry.get().strip())
            
            self.log_message(f"开始发送UDP数据包到 {target_ip}:{target_port}")
            self.log_message(f"数据包数量: {packet_count}, 发送间隔: {interval}秒")
            
            # 创建IPv4 UDP套接字
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            sent_count = 0
            for i in range(packet_count):
                if self.stop_sending:
                    self.log_message("用户请求停止发送")
                    break
                
                # 生成随机数据
                random_byte = bytes([random.randint(0, 255)])
                
                try:
                    sock.sendto(random_byte, (target_ip, target_port))
                    sent_count += 1
                    
                    if (i + 1) % 100 == 0:  # 每100个包更新一次日志
                        self.log_message(f"已发送 {i + 1}/{packet_count} 个数据包")
                    
                    # 添加延迟
                    if interval > 0:
                        time.sleep(interval)
                        
                except socket.error as e:
                    self.log_message(f"发送数据包时出错: {e}")
                    break
            
            sock.close()
            self.log_message(f"发送完成! 成功发送 {sent_count} 个UDP数据包")
            
        except Exception as e:
            self.log_message(f"发生错误: {e}")
        finally:
            # 恢复UI状态
            self.is_sending = False
            self.root.after(0, self.reset_ui)
    
    def reset_ui(self):
        """重置UI状态"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = UDPPacketSender(root)
    root.mainloop()
