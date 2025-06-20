import base64
import io
import threading
from socket import socket, AF_INET, SOCK_STREAM
from customtkinter import *
from tkinter import filedialog
from PIL import Image


class RegisterWindow(CTk):
    def __init__(self):
        super().__init__()
        self.username = None
        self.title('Вхід до чату')
        self.geometry('300x300')
        CTkLabel(self, text='LogiTalk', font= ('Arial', 25, 'bold')).pack(pady= 40)
        self.name_entry = CTkEntry(self, placeholder_text = "Введіть ім'я",width= 200)
        self.name_entry.pack(pady=5)
        self.host_entry = CTkEntry(self, placeholder_text = "Введіть хост сервера",width= 200)
        self.host_entry.pack(pady=5)
        self.port_entry = CTkEntry(self, placeholder_text="Введіть порт сервера",width= 200)
        self.port_entry.pack(pady=5)
        self.login_button = CTkButton(self, text='Приєднатися', command= self.start_chat)
        self.login_button.pack(pady= 10)

    def start_chat(self):
        self.username = self.name_entry.get()
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((self.host_entry.get(), int(self.port_entry.get())))
            hello = f"TEXT@ {self.username} @ {self.username} приєднався(лась) до чату!"
            self.sock.send(hello.encode('utf-8'))
            self.destroy()
            win = MainWindow(self.sock, self.username)
            win.mainloop()
        except Exception as e:
            print(f'Не вдалося приєднатися: {e}')



class MainWindow(CTk):
   def __init__(self, sock, username):
       super().__init__()
       self.username = username
       self.sock = sock
       self.geometry('400x300')
       self.title("Chat Client")
       self.label = None
       self.menu_frame = CTkFrame(self, width=30, height=300)
       self.menu_frame.pack_propagate(False)
       self.menu_frame.place(x=0, y=0)
       self.is_show_menu = False
       self.speed_animate_menu = -20
       self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
       self.btn.place(x=0, y=0)
       self.chat_field = CTkScrollableFrame(self)
       self.chat_field.place(x=0, y=0)
       self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
       self.message_entry.place(x=0, y=0)
       self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
       self.send_button.place(x=0, y=0)

       self.open_img_button = CTkButton(self, text='📂', width=50, height=40, command=self.open_image)
       self.open_img_button.place(x=0, y=0)
       self.adaptive_ui()
       threading.Thread(target=self.recv_message).start()

   def toggle_show_menu(self):
      if self.is_show_menu:
          self.is_show_menu = False
          self.speed_animate_menu *= -1
          self.btn.configure(text='▶️')
          self.show_menu()
      else:
          self.is_show_menu = True
          self.speed_animate_menu *= -1
          self.btn.configure(text='◀️')
          self.show_menu()
          self.label = CTkLabel(self.menu_frame, text='Імʼя')
          self.label.pack(pady=30)
          self.entry = CTkEntry(self.menu_frame, placeholder_text="Ваш нік...")
          self.entry.pack()
          self.save_button = CTkButton(self.menu_frame, text="Зберегти", command=self.save_name)
          self.save_button.pack()

   def show_menu(self):
      self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
      if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
          self.after(10, self.show_menu)
      elif self.menu_frame.winfo_width() >= 60 and not self.is_show_menu:
          self.after(10, self.show_menu)
          if self.label:
              self.label.destroy()
          if getattr(self, "entry", None):
              self.entry.destroy()
          if getattr(self, "save_button", None):
              self.save_button.destroy()

   def save_name(self):
      new_name = self.entry.get().strip()
      if new_name:
          self.username = new_name
          self.add_message(f"Ваш новий нік: {self.username}")

   def adaptive_ui(self):
      self.menu_frame.configure(height=self.winfo_height())
      self.chat_field.place(x=self.menu_frame.winfo_width())
      self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                height=self.winfo_height() - 40)
      self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
      self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
      self.message_entry.configure(
          width=self.winfo_width() - self.menu_frame.winfo_width() - 110)
      self.open_img_button.place(x=self.winfo_width()-105, y=self.send_button.winfo_y())
      self.after(50, self.adaptive_ui)

   def add_message(self, message, img=None):
      message_frame = CTkFrame(self.chat_field, fg_color='grey')
      message_frame.pack(pady=5, anchor='w')
      wrapleng_size = self.winfo_width() - self.menu_frame.winfo_width() - 40
      if not img:
          CTkLabel(message_frame, text=message, wraplength=wrapleng_size,
                   text_color='white', justify='left').pack(padx=10, pady=5)
      else:
          CTkLabel(message_frame, text=message, wraplength=wrapleng_size,
                   text_color='white', image=img, compound='top',
                   justify='left').pack(padx=10, pady=5)

   def send_message(self):
      message = self.message_entry.get()
      if message:
          self.add_message(f"{self.username}: {message}")
          data = f"TEXT@{self.username}@{message}\n"
          try:
              self.sock.sendall(data.encode())
          except:
              pass
      self.message_entry.delete(0, END)

   def recv_message(self):
      buffer = ""
      while True:
          try:
              chunk = self.sock.recv(4096)
              if not chunk:
                  break
              buffer += chunk.decode('utf-8', errors='ignore')
              while "\n" in buffer:
                  line, buffer = buffer.split("\n", 1)
                  self.handle_line(line.strip())
          except:
              break
      self.sock.close()

   def handle_line(self, line):
      if not line:
          return
      parts = line.split("@", 3)
      msg_type = parts[0]
      if msg_type == "TEXT":
          if len(parts) >= 3:
              author = parts[1]
              message = parts[2]
              self.add_message(f"{author}: {message}")
      elif msg_type == "IMAGE":
          if len(parts) >= 4:
              author = parts[1]
              filename = parts[2]
              b64_img = parts[3]
              try:
                  img_data = base64.b64decode(b64_img)
                  pil_img = Image.open(io.BytesIO(img_data))
                  ctk_img = CTkImage(pil_img, size=(300, 300))
                  self.add_message(f"{author} надіслав(ла) зображення: {filename}", img=ctk_img)
              except Exception as e:
                  self.add_message(f"Помилка відображення зображення: {e}")
      else:
          self.add_message(line)

   def open_image(self):
      file_name = filedialog.askopenfilename()
      if not file_name:
          return
      try:
          with open(file_name, "rb") as f:
              raw = f.read()
          try:
            b64_data = base64.b64encode(raw).decode()
            short_name = os.path.basename(file_name)
          except:
              print('помилка')
          data = f"IMAGE@{self.username}@{short_name}@{b64_data}\n"
          self.sock.sendall(data.encode())
          self.add_message('', CTkImage(light_image=Image.open(file_name), size=(300, 300)))
      except Exception as e:
          self.add_message(f"Не вдалося надіслати зображення: {e}")


logitalk = RegisterWindow()
logitalk.mainloop()