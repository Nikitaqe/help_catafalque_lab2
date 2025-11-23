import os
import shutil
import datetime
import stat
from logging_utils import setup_logging, log_command

class MiniShell:
    def __init__(self):
        self.current_dir = os.getcwd()
        setup_logging()
    
    def get_absolute_path(self, path):
        """Получение абсолютного пути"""
        if not path:
            return self.current_dir
        
        if path == "~":
            return os.path.expanduser("~")
        elif path.startswith("~"):
            return os.path.expanduser(path)
        
        if not os.path.isabs(path):
            return os.path.join(self.current_dir, path)
        return path
    
    def ls(self, args):
        """Команда ls - список файлов и каталогов"""
        path = self.current_dir
        detailed = False
        
        # Парсинг аргументов
        i = 0
        while i < len(args):
            if args[i] == "-l":
                detailed = True
            else:
                path = self.get_absolute_path(args[i])
            i += 1
        
        try:
            if not os.path.exists(path):
                error_msg = f"ls: {path}: No such file or directory"
                log_command(f"ls {' '.join(args)}", False, error_msg)
                print(error_msg)
                return
            
            if not os.path.isdir(path):
                error_msg = f"ls: {path}: Not a directory"
                log_command(f"ls {' '.join(args)}", False, error_msg)
                print(error_msg)
                return
            
            items = os.listdir(path)
            
            if detailed:
                for item in items:
                    item_path = os.path.join(path, item)
                    stat_info = os.stat(item_path)
                    
                    # Права доступа
                    permissions = stat.filemode(stat_info.st_mode)
                    
                    # Размер
                    size = stat_info.st_size
                    
                    # Дата изменения
                    mtime = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    
                    print(f"{permissions} {size:8} {mtime} {item}")
            else:
                for item in items:
                    print(item)
            
            log_command(f"ls {' '.join(args)}")
            
        except Exception as e:
            error_msg = str(e)
            log_command(f"ls {' '.join(args)}", False, error_msg)
            print(f"ls: error: {error_msg}")
    
    def cd(self, args):
        """Команда cd - смена каталога"""
        if len(args) == 0:
            new_path = os.path.expanduser("~")
        else:
            path = args[0]
            if path == "..":
                new_path = os.path.dirname(self.current_dir)
            elif path == "~":
                new_path = os.path.expanduser("~")
            else:
                new_path = self.get_absolute_path(path)
        
        try:
            if os.path.exists(new_path) and os.path.isdir(new_path):
                self.current_dir = os.path.abspath(new_path)
                os.chdir(self.current_dir)
                log_command(f"cd {' '.join(args)}")
            else:
                error_msg = f"cd: {new_path}: No such directory"
                log_command(f"cd {' '.join(args)}", False, error_msg)
                print(error_msg)
                
        except Exception as e:
            error_msg = str(e)
            log_command(f"cd {' '.join(args)}", False, error_msg)
            print(f"cd: error: {error_msg}")
    
    def cat(self, args):
        """Команда cat - вывод содержимого файла"""
        if len(args) == 0:
            error_msg = "cat: missing file name"
            log_command("cat", False, error_msg)
            print(error_msg)
            return
        
        file_path = self.get_absolute_path(args[0])
        
        try:
            if not os.path.exists(file_path):
                error_msg = f"cat: {file_path}: No such file or directory"
                log_command(f"cat {' '.join(args)}", False, error_msg)
                print(error_msg)
                return
            
            if os.path.isdir(file_path):
                error_msg = f"cat: {file_path}: Is a directory"
                log_command(f"cat {' '.join(args)}", False, error_msg)
                print(error_msg)
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
            
            log_command(f"cat {' '.join(args)}")
            
        except Exception as e:
            error_msg = str(e)
            log_command(f"cat {' '.join(args)}", False, error_msg)
            print(f"cat: error: {error_msg}")
    
    def cp(self, args):
        """Команда cp - копирование файлов/каталогов"""
        recursive = False
        sources = []
        
        # Парсинг аргументов
        i = 0
        while i < len(args):
            if args[i] == "-r":
                recursive = True
            else:
                sources.append(args[i])
            i += 1
        
        if len(sources) < 2:
            error_msg = "cp: missing source or destination"
            log_command(f"cp {' '.join(args)}", False, error_msg)
            print(error_msg)
            return
        
        source = self.get_absolute_path(sources[0])
        destination = self.get_absolute_path(sources[1])
        
        try:
            if not os.path.exists(source):
                error_msg = f"cp: {source}: No such file or directory"
                log_command(f"cp {' '.join(args)}", False, error_msg)
                print(error_msg)
                return
            
            if os.path.isdir(source) and not recursive:
                error_msg = f"cp: {source}: Is a directory (use -r)"
                log_command(f"cp {' '.join(args)}", False, error_msg)
                print(error_msg)
                return
            
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            
            log_command(f"cp {' '.join(args)}")
            print(f"Copied {source} to {destination}")
            
        except Exception as e:
            error_msg = str(e)
            log_command(f"cp {' '.join(args)}", False, error_msg)
            print(f"cp: error: {error_msg}")
    
    def mv(self, args):
        """Команда mv - перемещение/переименование"""
        if len(args) < 2:
            error_msg = "mv: missing source or destination"
            log_command(f"mv {' '.join(args)}", False, error_msg)
            print(error_msg)
            return
        
        source = self.get_absolute_path(args[0])
        destination = self.get_absolute_path(args[1])
        
        try:
            if not os.path.exists(source):
                error_msg = f"mv: {source}: No such file or directory"
                log_command(f"mv {' '.join(args)}", False, error_msg)
                print(error_msg)
                return
            
            shutil.move(source, destination)
            log_command(f"mv {' '.join(args)}")
            print(f"Moved {source} to {destination}")
            
        except Exception as e:
            error_msg = str(e)
            log_command(f"mv {' '.join(args)}", False, error_msg)
            print(f"mv: error: {error_msg}")
    
    def rm(self, args):
        """Команда rm - удаление файлов/каталогов"""
        recursive = False
        targets = []
        
        # Парсинг аргументов
        i = 0
        while i < len(args):
            if args[i] == "-r":
                recursive = True
            else:
                targets.append(args[i])
            i += 1
        
        if len(targets) == 0:
            error_msg = "rm: missing file or directory name"
            log_command(f"rm {' '.join(args)}", False, error_msg)
            print(error_msg)
            return
        
        target = self.get_absolute_path(targets[0])
        
        # Проверка безопасности
        if target in ["/", ".."] or os.path.abspath(target) == os.path.abspath("/"):
            error_msg = f"rm: cannot remove '{target}': Operation not permitted"
            log_command(f"rm {' '.join(args)}", False, error_msg)
            print(error_msg)
            return
        
        try:
            if not os.path.exists(target):
                error_msg = f"rm: {target}: No such file or directory"
                log_command(f"rm {' '.join(args)}", False, error_msg)
                print(error_msg)
                return
            
            if os.path.isdir(target):
                if not recursive:
                    error_msg = f"rm: {target}: Is a directory (use -r)"
                    log_command(f"rm {' '.join(args)}", False, error_msg)
                    print(error_msg)
                    return
                else:
                    # Запрос подтверждения для удаления каталога
                    response = input(f"rm: remove directory '{target}'? (y/n): ")
                    if response.lower() != 'y':
                        print("Operation cancelled")
                        return
                    shutil.rmtree(target)
            else:
                os.remove(target)
            
            log_command(f"rm {' '.join(args)}")
            print(f"Removed {target}")
            
        except Exception as e:
            error_msg = str(e)
            log_command(f"rm {' '.join(args)}", False, error_msg)
            print(f"rm: error: {error_msg}")
    
    def run(self):
        """Основной цикл оболочки"""
        print("Mini Shell started. Type 'exit' to quit.")
        
        while True:
            try:
                command_input = input(f"{self.current_dir}$ ").strip()
                
                if not command_input:
                    continue
                
                if command_input == "exit":
                    break
                
                parts = command_input.split()
                command = parts[0]
                args = parts[1:]
                
                if command == "ls":
                    self.ls(args)
                elif command == "cd":
                    self.cd(args)
                elif command == "cat":
                    self.cat(args)
                elif command == "cp":
                    self.cp(args)
                elif command == "mv":
                    self.mv(args)
                elif command == "rm":
                    self.rm(args)
                else:
                    error_msg = f"{command}: command not found"
                    log_command(command_input, False, error_msg)
                    print(error_msg)
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                error_msg = str(e)
                log_command(command_input if 'command_input' in locals() else "unknown", False, error_msg)
                print(f"Error: {error_msg}")