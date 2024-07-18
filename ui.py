import os
import sys
import tkinter as tk
import traceback
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import threading
import ui_service

service = ui_service.ui_service()

# Função para mostrar a janela de status
def show_status_window():
    status_window = tk.Toplevel(root)
    status_window.title("Atualização dos Mods")
    status_window.configure(bg='#2e2e2e')
    status_label = tk.Label(status_window, text="Iniciando a atualização dos mods...", bg='#2e2e2e', fg='white', font=('Helvetica', 14, 'bold'))
    status_label.pack(pady=20)
    status_listbox = tk.Listbox(status_window, bg='#3a3a3a', fg='white', font=('Helvetica', 12))
    status_listbox.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
    return status_window, status_label, status_listbox

# Função para alternar a remoção de mods antigos
def toggle_remove_old_mods():
    config['delete_mods'] = not config['delete_mods']
    service.config.save_config(config)
    update_switch()

def update_switch():
    if config['delete_mods']:
        switch_label.config(text="YES", bg="green")
    else:
        switch_label.config(text="NO", bg="red")

def update_mod_pack():
    status_window, status_label, status_listbox = show_status_window()
    threading.Thread(target=lambda: service.sync(tk, root, status_listbox, service.config.load_config()["mod_folder_path"])).start()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CONFIG_PATH = resource_path("config.json")

# Função para iniciar o jogo
def play_tsmp():
    print("Iniciar TSMP...")
    service.create_instance_directories()
    service.update_launcher_profiles()
    status_window, status_label, status_listbox = show_status_window()
    threading.Thread(target=lambda: service.sync(tk, root, status_listbox)).start()
    root.after(100, lambda: check_sync_complete(status_window))

# Função para verificar se a sincronização foi concluída
def check_sync_complete(status_window):
    if threading.active_count() > 1:
        root.after(100, lambda: check_sync_complete(status_window))
    else:
        status_window.destroy()
        service.run_minecraft()

# Função para selecionar uma nova pasta de mods
def select_mod_folder():
    folder_selected = filedialog.askdirectory(initialdir=config['mod_folder_path'])
    if folder_selected:
        config['mod_folder_path'] = folder_selected
        service.config.save_config(config)
        update_buttons_state()
        print(f"Nova pasta de mods selecionada: {folder_selected}")

def update_buttons_state():
    if config['mod_folder_path'] == '~':
        update_button.config(state=tk.DISABLED, image=click_btn2)
    else:
        update_button.config(state=tk.NORMAL, image=click_btn2)

try:
    config = service.config.load_config()

    # Criação da janela principal
    root = tk.Tk()
    root.title("TSMP Launcher")
    root.configure(bg='#2e2e2e')

    image_path = resource_path("logo_concept_maybe_idk_man.jpg")
    image = Image.open(image_path)
    image = image.resize((400, 400), Image.Resampling.LANCZOS)
    logo = ImageTk.PhotoImage(image)

    logo_label = tk.Label(root, image=logo, bg='#2e2e2e')
    logo_label.pack(pady=0,anchor='center')

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', background='#2e2e2e', foreground='white', font=('Helvetica', 12, 'bold'), borderwidth=0, focuscolor='#5c5c5c')
    style.map('TButton', background=[('active', '#6e6e6e')], foreground=[('active', 'white')])

    # Import the image using PhotoImage function
    click_btn = tk.PhotoImage(file='botao_tamanho_certo.png')

    # Centralizando o botão play TSMP
    #play_button = ttk.Button(root, image=click_btn, style='TButton', command=play_tsmp)
    #play_button.pack(pady=10, anchor='w')

    # Frame para o botão de update e a pastinha
    update_frame = tk.Frame(root, bg='#2e2e2e')
    update_frame.pack(pady=10, anchor='center')

    # Import the image using PhotoImage function
    click_btn2 = tk.PhotoImage(file='update_custom_folder.png')

    update_button = ttk.Button(update_frame, image=click_btn2, style='TButton', command=update_mod_pack)
    update_button.pack(side="left", padx=5, anchor='w')

    folder_icon = Image.open(resource_path("img.png")).resize((40, 40), Image.Resampling.LANCZOS)
    folder_icon = ImageTk.PhotoImage(folder_icon)

    select_folder_button = ttk.Button(update_frame, image=folder_icon, style='TButton', command=select_mod_folder)
    select_folder_button.pack(side="left", padx=5, anchor='w')

    # Centralizando o switch para remover mods antigos
    switch_frame = tk.Frame(root, bg='#2e2e2e')
    switch_frame.pack(pady=10, anchor='w')

    # Import the image using PhotoImage function
    click_btn3 = tk.PhotoImage(file='rewrite_mod_folder.png')

    switch_button = ttk.Button(switch_frame, image=click_btn3, style='TButton', command=toggle_remove_old_mods)
    switch_button.pack(side="left", padx=5, anchor='w')

    switch_label = tk.Label(switch_frame, text="", width=4, bg="red", fg="white", font=('Helvetica', 12, 'bold'))
    switch_label.pack(side="left", padx=5, anchor='w')

    # Centralizar os frames principais
    #play_button.pack(anchor='center')
    update_frame.pack(anchor='center')
    switch_frame.pack(anchor='center')
    switch_button.pack(anchor='center')
    update_button.pack(anchor='center')

    update_switch()
    update_buttons_state()

    root.geometry('400x700')
    root.eval('tk::PlaceWindow . center')

    root.mainloop()
except Exception as e:
    traceback.print_exception(e)
    wait_for_it = input('Press enter to close the terminal window')
