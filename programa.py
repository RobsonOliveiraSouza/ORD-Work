import sys
import os

class Game:
    def __init__(self, identifier, title, year, genre, producer, platform):
        self.identifier = identifier
        self.title = title
        self.year = year
        self.genre = genre
        self.producer = producer
        self.platform = platform

    def to_string(self, tamanho_registro: int) -> str:
        return f'{self.identifier}|{self.title}|{self.year}|{self.genre}|{self.producer}|{self.platform}| ({tamanho_registro} bytes)'

    def formatado(self) -> bytes:
        return f'{self.identifier}|{self.title}|{self.year}|{self.genre}|{self.producer}|{self.platform}|'.encode()

    @classmethod
    def from_bytes(cls, data):
        parts = data.split(b'|')
        if len(parts) < 6:
            raise ValueError("Dados incompletos para um jogo")

        identifier = parts[0].decode()
        title = parts[1].decode()
        year = int(parts[2].decode())
        genre = parts[3].decode()
        producer = parts[4].decode()
        platform = parts[5].decode()

        return cls(identifier, title, year, genre, producer, platform)

def leia_reg(file):
    try:
        bytes_registro = file.read(2)  # Lê o tamanho do registro (2 bytes)
        if not bytes_registro:
            return None
        tamanho_registro = int.from_bytes(bytes_registro)
        if tamanho_registro > 0:
            registro = file.read(tamanho_registro)
            return (tamanho_registro, registro)
        return None
    except Exception as e:
        print(f'Erro leia_reg: {e}')
        return None

def buscar_jogo_por_id(file, identificador):
    file.seek(4)
    while True:
        tamanho_registro_e_dados = leia_reg(file)
        if not tamanho_registro_e_dados:
            return None
        (tamanho_registro, registro) = tamanho_registro_e_dados
        game = Game.from_bytes(registro)
        if game.identifier == str(identificador):
            return (game, tamanho_registro)

def search_game(file, identifier):
    try:
        game_encontrado = buscar_jogo_por_id(file, identifier)
        if game_encontrado:
            (game, tamanho_registro) = game_encontrado
            print(f"{game.to_string(tamanho_registro)}")
        else:
            print(f"Jogo com identificador {identifier} não encontrado.")
    except ValueError as ve:
        print(f"Erro ao processar registro: {ve}")

def insert_game(file, game):
    try:
        file.seek(4)  # Pula o cabeçalho
        led = []

        while True:
            pos = file.tell()
            data = leia_reg(file)
            if data is None:
                break

            tamanho_registro, _ = data
            led.append((tamanho_registro, pos))

        # Ordena a LED para usar o maior espaço disponível (worst-fit)
        led.sort(reverse=True, key=lambda x: x[0])

        inserido = False
        novo_registro_bytes = game.formatado()
        tamanho_novo_registro = len(novo_registro_bytes)

        for tamanho_registro, pos in led:
            if tamanho_registro >= tamanho_novo_registro:
                file.seek(pos - tamanho_registro - 2)  # Ajusta posição para incluir os 2 bytes do tamanho
                file.write(tamanho_novo_registro.to_bytes(2, byteorder='big'))
                file.write(novo_registro_bytes.ljust(tamanho_registro, b'\0'))
                inserido = True
                break

        if not inserido:
            file.seek(0, os.SEEK_END)  # Vai para o final do arquivo
            pos = file.tell()
            file.write(tamanho_novo_registro.to_bytes(2, byteorder='big'))
            file.write(novo_registro_bytes)

        print(f"Inserção do registro de chave \"{game.identifier}\" ({tamanho_novo_registro} bytes)\nLocal: offset = {pos}")

        # Atualiza o total de registros
        file.seek(0)
        total_reg = int.from_bytes(file.read(4), byteorder='big') + 1
        file.seek(0)
        file.write(total_reg.to_bytes(4, byteorder='big'))

    except Exception as e:
        print(f'Erro insert_game: {e}')

def remove_game(file, identifier):
    try:
        file.seek(4)  # Pula o cabeçalho
        pos = file.tell()
        while True:
            data = leia_reg(file)
            if data is None:
                print(f"Jogo com identificador {identifier} não encontrado.")
                return

            tamanho_registro, registro = data
            game = Game.from_bytes(registro)

            if game.identifier == str(identifier):
                file.seek(pos - tamanho_registro - 2)  # Ajusta posição para incluir os 2 bytes do tamanho
                file.write((tamanho_registro).to_bytes(2, byteorder='big'))  # Grava o tamanho do espaço disponível
                file.write(b'\0' * tamanho_registro)  # Marca o espaço como disponível

                print(f"Remoção do registro de chave \"{identifier}\"\nRegistro removido! ({tamanho_registro} bytes)\nLocal: offset = {pos - tamanho_registro - 2}")
                return

            pos = file.tell()
    except Exception as e:
        print(f'Erro remove_game: {e}')

def print_led(file):
    try:
        file.seek(0)
        total_reg = int.from_bytes(file.read(4), byteorder='big')  # Lê o cabeçalho
        print(f"Total de registros: {total_reg}")

        file.seek(4)
        led = []
        while True:
            data = leia_reg(file)
            if data is None:
                break
            tamanho_registro, _ = data
            if tamanho_registro > 0:
                led.append((tamanho_registro, file.tell() - tamanho_registro - 2))

        if led:
            print("LED ->", end=' ')
            for tamanho, offset in led:
                print(f"[offset: {offset}, tam: {tamanho}] ->", end=' ')
            print("[offset: -1]")
            print(f"Total: {len(led)} espaços disponíveis")
        else:
            print("LED está vazia.")
    except Exception as e:
        print(f'Erro print_led: {e}')

def process_operations(file, arquivo_de_operacoes):
    for linha in arquivo_de_operacoes:
        linha_arquivo_operacoes = linha.strip().split(maxsplit=1)
        if not linha_arquivo_operacoes or len(linha_arquivo_operacoes) < 2:
            print(f"Operação inválida ou vazia: {linha}")
            continue

        comando, argumento = linha_arquivo_operacoes[0], linha_arquivo_operacoes[1]  # [b, 22] OU [i, <registro>] OU [d, 22], por exemplo
        match comando:
            case 'b':
                try:
                    identifier = int(argumento)
                    search_game(file, identifier)
                except ValueError:
                    print(f"Identificador de busca inválido: {argumento}")
            case 'i':
                try:
                    parts = argumento.split('|')
                    if len(parts) < 6:
                        raise ValueError("Dados incompletos para inserção.")

                    identifier, title, year, genre, producer, platform = parts[:6]
                    game = Game(identifier, title, int(year), genre, producer, platform)
                    insert_game(file, game)
                except ValueError as ve:
                    print(f"Erro ao processar inserção: {ve}")
            case 'r':
                try:
                    identifier = int(argumento)
                    remove_game(file, identifier)
                except ValueError:
                    print(f"Identificador de remoção inválido: {argumento}")
            case _:
                print(f"Comando desconhecido: {comando}")

def main(args):
    if len(args) < 2:
        print("Uso: programa.py -e <arquivo_de_operacoes> | -p")
        return

    if args[0] == '-e' and len(args) == 2:
        try:
            with open('dados.dat', 'rb+') as file:
                with open(args[1], 'r') as arquivo_de_operacoes:
                    process_operations(file, arquivo_de_operacoes)
        except FileNotFoundError:
            print("Erro: arquivo dados.dat não encontrado.")
    elif args[0] == '-p':
        try:
            with open('dados.dat', 'rb') as file:
                print_led(file)
        except FileNotFoundError:
            print("Erro: arquivo dados.dat não encontrado.")
    else:
        print("Uso: programa.py -e <arquivo_de_operacoes> | -p")

if __name__ == '__main__':
    main(sys.argv[1:])
