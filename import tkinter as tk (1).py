import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os
from pyngrok import ngrok
from datetime import datetime
import threading
import http.server
import socketserver

# Tạo cửa sổ Tkinter
root = tk.Tk()
root.title("Medical Application")

# Biến toàn cục để lưu folder của bệnh nhân
user_folder = ""

# Hàm để chụp ảnh
def capture_image():
    if user_folder:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            folder_path = f'./Patients/{user_folder}'
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            img_path = os.path.join(folder_path, 'image.jpg')
            cv2.imwrite(img_path, frame)
            cap.release()
            cv2.destroyAllWindows()
            messagebox.showinfo("Thông báo", f'Ảnh đã lưu tại: {img_path}')
        else:
            messagebox.showwarning("Lỗi", "Không thể mở camera")
    else:
        messagebox.showwarning("Lỗi", "Vui lòng tạo folder trước khi chụp ảnh")

# Hàm tạo folder cho người dùng
def create_folder():
    global user_folder
    name = name_entry.get().strip()
    dob = dob_entry.get().strip()
    cccd = cccd_entry.get().strip()

    if name and dob and cccd:
        try:
            # Chuyển ngày sinh về định dạng YYYYMMDD
            dob_formatted = datetime.strptime(dob, "%d/%m/%Y").strftime("%Y%m%d")
            # Lấy 4 số cuối của CCCD
            last_4_cccd = cccd[-4:]
            user_folder = f"{name}_{last_4_cccd}_{dob_formatted}"
            folder_path = f'./Patients/{user_folder}'
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                messagebox.showinfo("Thông báo", f"Folder đã tạo: {folder_path}")
            else:
                messagebox.showwarning("Cảnh báo", "Folder đã tồn tại, tiếp tục cập nhật thông tin.")
        except ValueError:
            messagebox.showwarning("Lỗi", "Ngày sinh không đúng định dạng (DD/MM/YYYY)")
    else:
        messagebox.showwarning("Lỗi", "Vui lòng nhập tên, ngày sinh và CCCD")

def save_patient_info():
    if user_folder:
        folder_path = f'./Patients/{user_folder}'
        info_path = os.path.join(folder_path, 'info.html')
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write(f"""
            <!DOCTYPE html>
            <html lang="vi">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Thông tin bệnh nhân</title>
            </head>
            <body>
            <h1>Thông tin bệnh nhân</h1>
            <p><strong>Tên bệnh nhân:</strong> {name_entry.get()}</p>
            <p><strong>Ngày sinh:</strong> {dob_entry.get()}</p>
            <p><strong>CCCD:</strong> {cccd_entry.get()}</p>
            <p>Thông tin khác có thể thêm ở đây</p>
            </body>
            </html>
            """)
        messagebox.showinfo("Thông báo", f"Thông tin đã lưu tại: {info_path}")

        # Tạo HTTP tunnel với ngrok và in đường dẫn ra terminal
        public_url = ngrok.connect(8000)
        print(f"Đường dẫn ngrok: {public_url}")
    else:
        messagebox.showwarning("Lỗi", "Folder chưa được tạo")

# Hàm khởi động server HTTP cho phép truy cập vào folder bệnh nhân
def start_server():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), Handler)
    print("Server bắt đầu chạy tại port", PORT)
    httpd.serve_forever()

# Chạy server trong luồng khác
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

# Giao diện nhập tên, ngày sinh và CCCD
tk.Label(root, text="Nhập tên bệnh nhân:").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Nhập ngày sinh (DD/MM/YYYY):").pack()
dob_entry = tk.Entry(root)
dob_entry.pack()

tk.Label(root, text="Nhập CCCD:").pack()
cccd_entry = tk.Entry(root)
cccd_entry.pack()

# Nút tạo folder
tk.Button(root, text="Tạo Folder", command=create_folder).pack()

# Nút chụp ảnh
tk.Button(root, text="Chụp ảnh", command=capture_image).pack()

# Nút lưu thông tin bệnh nhân
tk.Button(root, text="Lưu thông tin", command=save_patient_info).pack()

# Khởi động Tkinter
root.mainloop()
