import socket
import threading
import sys
import os
import platform
import subprocess

def get_processor_id():
    system_platform = platform.system()
    
    if system_platform == "Linux":
        # 对于 Linux 系统，从 /proc/cpuinfo 获取处理器ID
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if "Serial" in line:
                        return line.split(":")[1].strip()  # 返回序列号作为处理器ID
        except FileNotFoundError:
            print("无法读取 /proc/cpuinfo 文件")
            return None

    elif system_platform == "Windows" or "MSYS" in system_platform:
        # 对于 Windows 系统，使用 wmic 命令获取处理器ID
        try:
            output = subprocess.check_output("wmic cpu get processorId", shell=True)
            return output.decode().split("\n")[1].strip()  # 获取并清理结果
        except subprocess.CalledProcessError:
            print("无法获取 Windows 上的处理器 ID")
            return None

    elif system_platform == "Darwin":
        # 对于 macOS，使用 sysctl 获取 CPU 信息
        try:
            output = subprocess.check_output(["sysctl", "hw.model"])
            return output.decode().split(":")[1].strip()  # 返回处理器型号
        except subprocess.CalledProcessError:
            print("无法获取 macOS 上的处理器 ID")
            return None

    else:
        print(f"不支持的平台：{system_platform}")
        return None
class TCPServer:
    def __init__(self, host='127.0.0.1', port=65432, default_upload_dir='./upload'):
        self.host = host
        self.port = port
        self.server_socket = None
        self.default_upload_dir = default_upload_dir

        if not os.path.exists(self.default_upload_dir):
            os.makedirs(self.default_upload_dir)  # 创建上传目录

    def start(self):
        # 创建 TCP 套接字
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"服务器启动，监听 {self.host}:{self.port}")

        # 等待并接收客户端连接
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"连接来自 {client_address}")
            
            # 启动新线程处理客户端请求
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()
    def recv_length_prefixed_data(self, client_socket):
        """接收前缀长度的数据"""
        length_data = client_socket.recv(4)  # 首先接收4字节的长度信息
        print(length_data)
        if len(length_data) < 4:
            return None
        length = int.from_bytes(length_data, byteorder='big')  # 将字节转换为整数
        data = client_socket.recv(length)
        print(data)
        return data
    def handle_client(self, client_socket):
        try:
            # 接收处理器 ID
            processor_id = self.recv_length_prefixed_data(client_socket).decode('utf-8')
            print(f"接收到处理器 ID: {processor_id}")
            is_upload_file = self.recv_length_prefixed_data(client_socket)
  
            print(is_upload_file)
            if is_upload_file[0]==2:
                # 接收文件名
                filename = self.recv_length_prefixed_data(client_socket).decode('utf-8')
                print(f"接收到文件名: {filename}")

                # 接收目标目录（可选参数）
                target_dir = self.recv_length_prefixed_data(client_socket).decode('utf-8')
                if not target_dir:
                    target_dir = self.default_upload_dir  # 如果没有指定目录，使用默认目录

                # 创建目标目录（如果不存在）
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                
                # 拼接完整的文件路径
                file_path = os.path.join(target_dir, filename)

                # 开始接收文件内容并保存
                with open(file_path, 'wb') as file:
                    while True:
                        file_data = self.recv_length_prefixed_data(client_socket)
                        if not file_data:
                            break  # 接收完毕
                        file.write(file_data)
                
                print(f"文件 {filename} 已保存到 {target_dir} (处理器 ID: {processor_id})")
            else:
                print(f"end:{processor_id}")
        finally:
            client_socket.close()

    def stop(self):
        if self.server_socket:
            self.server_socket.close()
            print("服务器已停止")
class TCPClient:
    def __init__(self, host='127.0.0.1', port=65432, filename=None, target_dir='./upload'):
        self.host = host
        self.port = port
        self.filename = filename
        self.target_dir = target_dir
        self.processor_id = get_processor_id()  # 获取处理器 ID
        self.client_socket = None

    def connect(self):
        # 创建 TCP 套接字
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        print(f"已连接到服务器 {self.host}:{self.port}")
    def send_length_prefixed_data(self, data):
        """发送前缀长度的消息，先发送数据长度，再发送数据"""
        length = len(data)
        self.client_socket.send(length.to_bytes(4, byteorder='big'))  # 发送4字节长度
        self.client_socket.send(data)
    def send_file(self):
        
        
        # 发送处理器 ID 和文件名
        self.send_length_prefixed_data(self.processor_id.encode('utf-8'))  # 发送处理器 ID
        
        if self.filename == None:
            self.send_length_prefixed_data(b'\x01')
        else:
            self.send_length_prefixed_data(b'\x02')
            filename = os.path.basename(self.filename)
            # 检查文件是否存在
            if not os.path.isfile(filename):
                print(f"文件 {self.filename} 不存在！")
                return
            self.send_length_prefixed_data(filename.encode('utf-8'))  # 发送文件名
            self.send_length_prefixed_data(self.target_dir.encode('utf-8'))  # 发送目标目录

            # 打开文件并发送内容
            with open(self.filename, 'rb') as file:
                file_data = file.read(1020)
                while file_data:
                    self.send_length_prefixed_data(file_data)  # 发送文件内容
                    file_data = file.read(1020)  # 读取下一个块
                print(f"文件 {filename} 发送完毕！")

            # 关闭文件传输
            self.client_socket.send(b'')  # 发送空字节表示文件结束
            print("文件发送结束")

    def close(self):
        # 关闭客户端连接
        self.client_socket.close()
        print("连接已关闭")


def main():
    if len(sys.argv) < 2:
        print("请指定运行模式：'server' 或 'client'")
        return
    
    mode = sys.argv[1]
    target_dir="./upload"
    filename = sys.argv[2] if len(sys.argv) > 2 else None
    if mode == "server":
        # 启动服务端
        server = TCPServer(host='127.0.0.1', port=65432)
        server_thread = threading.Thread(target=server.start)
        server_thread.start()
    elif mode == "client":
        # 启动客户端
        client = TCPClient(host='127.0.0.1', port=65432, filename=filename, target_dir=target_dir)
        client.connect()
        client.send_file()
        client.close()
    else:
        print("无效模式，请选择 'server' 或 'client'")
if __name__=='__main__':
    main()
