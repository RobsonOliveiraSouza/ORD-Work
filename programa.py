import struct
import sys

class Game:
    def __init__(self, identifier, title, year, genre, producer, platform):
        self.identifier = identifier
        self.title = title
        self.year = year
        self.genre = genre
        self.producer = producer
        self.platform = platform

    def to_bytes(self):
        identifier_bytes = self.identifier.encode('utf-8')
        title_bytes = self.title.encode('utf-8')
        year_bytes = str(self.year).encode('utf-8')
        genre_bytes = self.genre.encode('utf-8')
        producer_bytes = self.producer.encode('utf-8')
        platform_bytes = self.platform.encode('utf-8')
        
        return identifier_bytes + b'|' + title_bytes + b'|' + year_bytes + b'|' + genre_bytes + b'|' + producer_bytes + b'|' + platform_bytes + b'|'

    @classmethod
    def from_bytes(cls, data):
        parts = data.split(b'|')
        if len(parts) < 6:
            raise ValueError("Dados incompletos para um jogo")

        identifier = parts[0].decode('utf-8')
        title = parts[1].decode('utf-8')
        try:
            year = int(parts[2].decode('utf-8'))
        except ValueError:
            year = 0  # Define um valor padrão para o ano inválido

        genre = parts[3].decode('utf-8')
        producer = parts[4].decode('utf-8')
        platform = parts[5].decode('utf-8')

        return cls(identifier, title, year, genre, producer, platform)

def leia_reg(file):
    try:
        tam_bytes = file.read(2)
        if not tam_bytes:
            return None
        tam = int.from_bytes(tam_bytes, byteorder='little')
        if tam > 0:
            s = file.read(tam)
            return s
        return None
    except Exception as e:
        print(f'Erro leia_reg: {e}')
        return None

def buscar_jogo_por_id(file, identificador):
    # Lê os 4 bytes do cabeçalho
    file.seek(4)
    while True:
        registro_data = leia_reg(file)
        if not registro_data:
            return None
        try:
            game = Game.from_bytes(registro_data)
            if game.identifier == str(identificador):
                return game
        except Exception as e:
            print(f'Erro ao processar registro: {e}')
            continue

def search_game(file, identifier):
    try:
        game = buscar_jogo_por_id(file, identifier)
        if game:
            print(f"{game.identifier}|{game.title}|{game.year}|{game.genre}|{game.producer}|{game.platform}")
        else:
            print(f"Jogo com identificador {identifier} não encontrado.")
    except ValueError as ve:
        print(f"Erro ao processar registro: {ve}")

def insert_game(file, game):
    pass

def remove_game(file, identifier):
    pass

def print_led(file):
    pass

def process_operations(file, operations):
    for operation in operations:
        op = operation.strip().split(maxsplit=1)
        if not op or len(op) < 2:
            print(f"Operação inválida ou vazia: {operation}")
            continue

        command = op[0]
        arguments = op[1]

        if command == 'b':
            try:
                identifier = int(arguments)
                search_game(file, identifier)
            except ValueError:
                print(f"Identificador inválido para busca: {arguments}")
        elif command == 'i':
            game_data = arguments.split('|')
            if len(game_data) == 6:
                try:
                    game = Game(game_data[0], game_data[1], int(game_data[2]), game_data[3], game_data[4], game_data[5])
                    insert_game(file, game)
                except ValueError as ve:
                    print(f"Erro ao inserir jogo: {ve}")
            else:
                print(f"Dados incompletos para inserção de jogo: {arguments}")
        elif command == 'r':
            try:
                identifier = int(arguments)
                remove_game(file, identifier)
            except ValueError:
                print(f"Identificador inválido para remoção: {arguments}")
        else:
            print(f"Operação não reconhecida: {operation}")

def main():
    if len(sys.argv) < 3:
        print("Uso: python programa.py -e arquivo_operacoes")
        return

    mode = sys.argv[1]
    operations_file = sys.argv[2]

    try:
        with open('dados.dat', 'r+b') as file:
            if mode == '-e':
                with open(operations_file, 'r') as ops:
                    operations = ops.readlines()
                    process_operations(file, operations)
            elif mode == '-p':
                print_led(file)
    except FileNotFoundError:
        print("Erro: arquivo dados.dat não encontrado.")

if __name__ == "__main__":
    main()
