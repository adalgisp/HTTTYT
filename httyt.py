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
img_path = ""

# Hàm để chụp ảnh
def capture_image():
    global img_path
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

# Hàm lưu thông tin bệnh nhân dưới dạng file HTML và hiển thị đường dẫn ngrok
def save_patient_info():
    if user_folder:
        folder_path = f'./Patients/{user_folder}'
        info_path = os.path.join(folder_path, 'info.html')
        with open(info_path, 'w', encoding='utf-8') as f:
            insurance_status = "Có bảo hiểm" if insurance_var.get() else "Không có bảo hiểm"
            gender = gender_var.get()
            img_html = f'<img src="image.jpg" alt="Ảnh bệnh nhân" width="200" height="200">' if img_path else "Chưa có ảnh"
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
            <p><strong>Cân nặng:</strong> {weight_entry.get()} kg</p>
            <p><strong>Chiều cao:</strong> {height_entry.get()} cm</p>
            <p><strong>Giới tính:</strong> {gender}</p>
            <p><strong>Bảo hiểm:</strong> {insurance_status}</p>
            <p><strong>Ảnh bệnh nhân:</strong> {img_html}</p>
            </body>
            </html>
            """)
        messagebox.showinfo("Thông báo", f"Thông tin đã lưu tại: {info_path}")

        # Tạo HTTP tunnel với ngrok và in đường dẫn ra terminal
        public_url = ngrok.connect(8000)
        print(f"Đường dẫn ngrok: {public_url}")

        # Xóa các dữ liệu đã nhập để bệnh nhân tiếp theo có thể điền
        clear_entries()

    else:
        messagebox.showwarning("Lỗi", "Folder chưa được tạo")

# Hàm xóa dữ liệu nhập sau khi gửi
def clear_entries():
    name_entry.delete(0, tk.END)
    dob_entry.delete(0, tk.END)
    cccd_entry.delete(0, tk.END)
    weight_entry.delete(0, tk.END)
    height_entry.delete(0, tk.END)
    insurance_var.set(0)
    gender_var.set("")

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

# Giao diện nhập thông tin bệnh nhân
tk.Label(root, text="Nhập tên bệnh nhân:").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Nhập ngày sinh (DD/MM/YYYY):").pack()
dob_entry = tk.Entry(root)
dob_entry.pack()

tk.Label(root, text="Nhập CCCD:").pack()
cccd_entry = tk.Entry(root)
cccd_entry.pack()

tk.Label(root, text="Nhập cân nặng (kg):").pack()
weight_entry = tk.Entry(root)
weight_entry.pack()

tk.Label(root, text="Nhập chiều cao (cm):").pack()
height_entry = tk.Entry(root)
height_entry.pack()

# Chọn giới tính
gender_var = tk.StringVar()
tk.Label(root, text="Chọn giới tính:").pack()
tk.Radiobutton(root, text="Nam", variable=gender_var, value="Nam").pack()
tk.Radiobutton(root, text="Nữ", variable=gender_var, value="Nữ").pack()

# Checkbox có bảo hiểm hay không
insurance_var = tk.IntVar()
tk.Checkbutton(root, text="Có bảo hiểm", variable=insurance_var).pack()

# Nút tạo folder
tk.Button(root, text="Tạo Folder", command=create_folder).pack()

# Nút chụp ảnh
tk.Button(root, text="Chụp ảnh", command=capture_image).pack()

# Nút lưu thông tin bệnh nhân
tk.Button(root, text="Lưu thông tin", command=save_patient_info).pack()

# Khởi động Tkinter
root.mainloop()
