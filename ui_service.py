import json
import os
import subprocess
import threading
import requests
import config_service


# Caminho para o launcher_profiles.json
launcher_profiles_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", ".minecraft", "tsmpinstace", "launcher_profiles.json")
forge_version = "1.20.1-forge-47.2.0"  # Substitua pela versão correta do Forge
instance_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", ".minecraft", "tsmpinstace2")
mods_path = os.path.join(instance_path, "mods")
minecraft_launcher_path = "C:\\XboxGames\\Minecraft Launcher\\Content\\gamelaunchhelper.exe"
repo_url = 'https://github.com/TORTUGASMP/MODS'


class ui_service():
    def __init__(self):
        self.config = config_service.config_service()

    def update_launcher_profiles(self):
        profiles = {}

        if os.path.exists(launcher_profiles_path):
            try:
                with open(launcher_profiles_path, 'r') as f:
                    if os.path.getsize(launcher_profiles_path) > 0:
                        profiles = json.load(f)
            except json.JSONDecodeError:
                print("The file launcher_profiles.json is empty or corrupted. Creating a new profile.")

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
            print("Custom profile added to launcher_profiles.json.")
        except Exception as e:
            print(f"Error on updating launcher_profiles.json: {str(e)}")

    def create_instance_directories(self):
        try:
            os.makedirs(instance_path, exist_ok=True)
            os.makedirs(mods_path, exist_ok=True)
            print(f"Diretório da instância customizada e da pasta de mods criado em {instance_path}.")
        except Exception as e:
            print(f"Erro ao criar o diretório da instância customizada: {str(e)}")


    # Função para executar o Minecraft Launcher com o perfil customizado
    def run_minecraft(self):
        try:
            subprocess.run([minecraft_launcher_path, "--workDir", instance_path])
            print("Minecraft Launcher executado com sucesso.")
        except Exception as e:
            print(f"Erro ao executar o Minecraft Launcher: {str(e)}")

    # Função para sincronizar mods e atualizar a janela de status
    def sync(self, tk, root, status_listbox, path = ''):
        repo_url = 'https://github.com/TORTUGASMP/MODS'
        if(path == ''):
            local_mods_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", ".minecraft", "tsmpinstace", "mods")
        else:
            local_mods_dir = path

        def log_status(message):
            status_listbox.insert(tk.END, message)
            status_listbox.yview(tk.END)  # Auto scroll to the end
            root.update_idletasks()  # Atualiza a UI

        log_status("checking repo files...")
        github_files = self.list_github_files(repo_url)
        local_files = os.listdir(local_mods_dir)

        # Baixar arquivos faltantes
        for file_name in github_files:
            if file_name not in local_files:
                log_status(f"Downloading File: {file_name}")
                self.download_github_file(repo_url, file_name, local_mods_dir)

        if(self.config.load_config()['delete_mods']):
            # Remover arquivos em excesso
            for file_name in local_files:
                if file_name not in github_files:
                    log_status(f"Removing File: {file_name}")
                    os.remove(os.path.join(local_mods_dir, file_name))

        log_status("Mod updates done. Close this windows if it does not close automatically")

    # Função para listar arquivos no repositório GitHub
    def list_github_files(self, repo_url, branch='1.20.1'):
        # Extrai "TORTUGASMP/MODS" corretamente
        owner_repo = '/'.join(repo_url.rstrip('/').split('/')[-2:])
        api_url = f'https://api.github.com/repos/{owner_repo}/contents'
        params = {'ref': branch}
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        return [file_info['name'] for file_info in response.json() if file_info['type'] == 'file']

    # Função para baixar arquivos do GitHub
    def download_github_file(self, repo_url, file_name, download_dir, branch='1.20.1'):
        owner_repo = '/'.join(repo_url.rstrip('/').split('/')[-2:])
        raw_url = f'https://raw.githubusercontent.com/{owner_repo}/{branch}/{file_name}'
        response = requests.get(raw_url)
        response.raise_for_status()

        os.makedirs(download_dir, exist_ok=True)
        local_path = os.path.join(download_dir, file_name)
        with open(local_path, 'wb') as f:
            f.write(response.content)

    # Função para sincronizar arquivos
    def sync_mods_with_github(self, repo_url, local_mods_dir, branch='1.20.1'):
        github_files = self.list_github_files(repo_url, branch)
        local_files = os.listdir(local_mods_dir)

        # Baixar arquivos faltantes
        for file_name in github_files:
            if file_name not in local_files:
                print(f"Baixando arquivo: {file_name}")
                self.download_github_file(repo_url, file_name, local_mods_dir, branch)

        # Remover arquivos em excesso
        for file_name in local_files:
            if file_name not in github_files:
                file_path = os.path.join(local_mods_dir, file_name)
                print(f"Removendo arquivo: {file_name}")
                os.remove(file_path)