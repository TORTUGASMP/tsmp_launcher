import json
import os
import subprocess
import time
from tkinter import filedialog

import psutil
import requests
from urllib.parse import urljoin

DEFAULT_CONFIG = {
    "mod_folder_path": "~",
    "download_mods": True,
    "delete_mods": True
}

# Caminho para o launcher_profiles.json
launcher_profiles_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", ".minecraft", "tsmpinstace", "launcher_profiles.json")

# Caminho para o diretório customizado do Minecraft
instance_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", ".minecraft", "tsmpinstace2")

# Caminho para a pasta de mods
mods_path = os.path.join(instance_path, "mods")

# Caminho para o Minecraft Launcher
minecraft_launcher_path = "C:\\XboxGames\\Minecraft Launcher\\Content\\gamelaunchhelper.exe"

# Versão do Minecraft que você deseja usar
minecraft_version = "1.20.1"
forge_version = "1.20.1-forge-47.2.0"  # Substitua pela versão correta do Forge
forge_installer_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-47.2.0/forge-1.20.1-47.2.0-installer.jar"  # Substitua pelo URL correto do instalador

#caminho de configuração do projeto:
CONFIG_PATH = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "TSMP_Launcher", "config.json")

def create_config():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as config_file:
        json.dump(DEFAULT_CONFIG, config_file, indent=4)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        create_config()
    with open(CONFIG_PATH, 'r') as config_file:
        return json.load(config_file)

# Função para verificar e instalar o Forge
def check_and_install_forge():
    forge_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", ".minecraft", "tsmpinstace", forge_version)
    if not os.path.exists(forge_dir):
        print("Forge não está instalado. Instalando Forge...")
        install_forge()

def install_forge():
    # Baixar o instalador do Forge
    installer_path = os.path.join(instance_path, "forge_installer.jar")
    response = requests.get(forge_installer_url)
    with open(installer_path, 'wb') as file:
        file.write(response.content)

    # Executar o instalador do Forge
    subprocess.run(['java', '-jar', installer_path, '--installClient'])

    # Remover o instalador do Forge após a instalação
    os.remove(installer_path)
    print("Forge instalado com sucesso.")

# Função para finalizar todos os processos do Minecraft Launcher
def terminate_minecraft_launcher_processes():
    for proc in psutil.process_iter(['pid', 'name']):
        if 'MinecraftLauncher' in proc.info['name']:
            proc.kill()

# Função para criar ou atualizar o launcher_profiles.json
def update_launcher_profiles():
    terminate_minecraft_launcher_processes()
    time.sleep(2)  # Espera para garantir que os processos foram finalizados

    profiles = {}

    if os.path.exists(launcher_profiles_path):
        try:
            with open(launcher_profiles_path, 'r') as f:
                if os.path.getsize(launcher_profiles_path) > 0:
                    profiles = json.load(f)
        except json.JSONDecodeError:
            print("O arquivo launcher_profiles.json estava vazio ou corrompido. Criando um novo perfil.")

    if 'profiles' not in profiles:
        profiles['profiles'] = {}

    profiles['profiles']['custom_instance'] = {
        "name": "tsmp modpack",
        "lastVersionId": forge_version,
        "gameDir": instance_path,
        "javaArgs": "-Xmx3G -Xms3G",
        "type": "custom"
    }

    try:
        with open(launcher_profiles_path, 'w') as f:
            json.dump(profiles, f, indent=4)
        print("Perfil customizado adicionado com sucesso ao launcher_profiles.json.")
    except Exception as e:
        print(f"Erro ao atualizar launcher_profiles.json: {str(e)}")

# Função para criar a estrutura de diretórios necessária
def create_instance_directories():
    try:
        os.makedirs(instance_path, exist_ok=True)
        os.makedirs(mods_path, exist_ok=True)
        print(f"Diretório da instância customizada e da pasta de mods criado em {instance_path}.")
    except Exception as e:
        print(f"Erro ao criar o diretório da instância customizada: {str(e)}")

# Função para copiar os mods para a pasta de mods
def copy_mods_to_instance(mods_source_path):
    try:
        if os.path.exists(mods_source_path):
            for mod_file in os.listdir(mods_source_path):
                full_file_path = os.path.join(mods_source_path, mod_file)
                if os.path.isfile(full_file_path):
                    subprocess.run(['copy', full_file_path, mods_path], shell=True)
            print(f"Mods copiados de {mods_source_path} para {mods_path}.")
        else:
            print(f"A pasta de mods fonte {mods_source_path} não foi encontrada.")
    except Exception as e:
        print(f"Erro ao copiar mods: {str(e)}")

# Função para executar o Minecraft Launcher com o perfil customizado
def run_minecraft():
    try:
        subprocess.run([minecraft_launcher_path, "--workDir", instance_path])
        print("Minecraft Launcher executado com sucesso.")
    except Exception as e:
        print(f"Erro ao executar o Minecraft Launcher: {str(e)}")


# Função para listar arquivos no repositório GitHub
def list_github_files(repo_url, branch='1.20.1'):
    # Extrai "TORTUGASMP/MODS" corretamente
    owner_repo = '/'.join(repo_url.rstrip('/').split('/')[-2:])
    api_url = f'https://api.github.com/repos/{owner_repo}/contents'
    params = {'ref': branch}
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    return [file_info['name'] for file_info in response.json() if file_info['type'] == 'file']

# Função para baixar arquivos do GitHub
def download_github_file(repo_url, file_name, download_dir, branch='1.20.1'):
    owner_repo = '/'.join(repo_url.rstrip('/').split('/')[-2:])
    raw_url = f'https://raw.githubusercontent.com/{owner_repo}/{branch}/{file_name}'
    response = requests.get(raw_url)
    response.raise_for_status()

    os.makedirs(download_dir, exist_ok=True)
    local_path = os.path.join(download_dir, file_name)
    with open(local_path, 'wb') as f:
        f.write(response.content)

# Função para sincronizar arquivos
def sync_mods_with_github(repo_url, local_mods_dir, branch='1.20.1'):
    github_files = list_github_files(repo_url, branch)
    local_files = os.listdir(local_mods_dir)

    # Baixar arquivos faltantes
    for file_name in github_files:
        if file_name not in local_files:
            print(f"Baixando arquivo: {file_name}")
            download_github_file(repo_url, file_name, local_mods_dir, branch)

    # Remover arquivos em excesso
    for file_name in local_files:
        if file_name not in github_files:
            file_path = os.path.join(local_mods_dir, file_name)
            print(f"Removendo arquivo: {file_name}")
            os.remove(file_path)

# Função para sincronizar mods e atualizar a janela de status
def synch(tk, root, status_listbox):
    repo_url = 'https://github.com/TORTUGASMP/MODS'
    local_mods_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", ".minecraft", "tsmpinstace", "mods")

    def log_status(message):
        status_listbox.insert(tk.END, message)
        status_listbox.yview(tk.END)  # Auto scroll to the end
        root.update_idletasks()  # Atualiza a UI

    log_status("Verificando arquivos no repositório...")
    github_files = list_github_files(repo_url)
    local_files = os.listdir(local_mods_dir)

    # Baixar arquivos faltantes
    for file_name in github_files:
        if file_name not in local_files:
            log_status(f"Baixando arquivo: {file_name}")
            download_github_file(repo_url, file_name, local_mods_dir)

    # Remover arquivos em excesso
    for file_name in local_files:
        if file_name not in github_files:
            log_status(f"Removendo arquivo: {file_name}")
            os.remove(os.path.join(local_mods_dir, file_name))

    log_status("Atualização dos mods concluída.")

def update_custom_mod_folder():
    sync_mods_with_github()


def open_mod_folder():
    mod_folder = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", ".minecraft", "custom_instance", "mods")
    if not os.path.exists(mod_folder):
        os.makedirs(mod_folder)
    os.startfile(mod_folder)

#if __name__ == "__main__":
#    create_instance_directories()
#    update_launcher_profiles()
#    run_minecraft()
