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
            print(f"Erro ao converter ano: {parts[2].decode('utf-8')}")
            raise ValueError(f"Ano inválido: {parts[2].decode('utf-8')}")

        genre = parts[3].decode('utf-8')
        producer = parts[4].decode('utf-8')
        platform = parts[5].decode('utf-8')
        
        return cls(identifier, title, year, genre, producer, platform)

def read_game(file, offset):
    file.seek(offset)
    tamanho_registro_bytes = file.read(2)
    if not tamanho_registro_bytes:
        return None
    
    tamanho_registro = struct.unpack('<H', tamanho_registro_bytes)[0]
    record_data = file.read(tamanho_registro)
    return Game.from_bytes(record_data)

def buscar_jogo_por_id(file, identificador):
    # Definindo o tamanho máximo esperado para um registro (ajuste conforme necessário)
    tamanho_maximo_registro = 256

    # Calculando o offset baseado no identificador
    offset = (identificador - 1) * tamanho_maximo_registro

    # Lendo o registro
    registro_data = ler_registro(file, offset)

    if registro_data:
        game = Game.from_bytes(registro_data)
        return game
    else:
        return None

def ler_registro(file, offset):
    # Definindo a estrutura do registro
    registro_formato = "<4si64s64s64s64s"

    # Movendo o cursor para o offset especificado
    file.seek(offset)

    try:
        # Lendo os dados do registro
        registro = struct.unpack(registro_formato, file.read(struct.calcsize(registro_formato)))
        
        # Decodificando os campos para strings corretas
        identifier = registro[0].decode('utf-8').strip('\x00')
        year = registro[1]
        title = registro[2].decode('utf-8').strip('\x00')
        genre = registro[3].decode('utf-8').strip('\x00')
        producer = registro[4].decode('utf-8').strip('\x00')
        platform = registro[5].decode('utf-8').strip('\x00')

        return (identifier, year, title, genre, producer, platform)
    except struct.error:
        return None

def search_game(file, identifier):
    try:
        with open('dados.dat', 'rb') as file:
            # Definindo o tamanho do registro (está definido como 264 bytes no seu exemplo)
            tamanho_registro = 264
            offset = (identifier - 1) * tamanho_registro  # Calculando o offset baseado no identificador

            # Lendo o registro
            registro = ler_registro(file, offset)

            if registro:
                print(f"{identifier}|{registro[2]}|{registro[1]}|{registro[3]}|{registro[4]}|{registro[5]}| ({tamanho_registro} bytes)")
            else:
                print(f"Jogo com identificador {identifier} não encontrado.")
    except ValueError as ve:
        print(f"Erro ao processar registro: {ve}")
def search_game(file, identifier):
    try:
        with open('dados.dat', 'rb') as file:
            # Definindo o tamanho do registro (está definido como 264 bytes no seu exemplo)
            tamanho_registro = 264
            offset = (identifier - 1) * tamanho_registro  # Calculando o offset baseado no identificador

            # Lendo o registro
            registro = ler_registro(file, offset)

            if registro:
                print(f"{identifier}|{registro[2]}|{registro[1]}|{registro[3]}|{registro[4]}|{registro[5]}| ({tamanho_registro} bytes)")
            else:
                print(f"Jogo com identificador {identifier} não encontrado.")
    except ValueError as ve:
        print(f"Erro ao processar registro: {ve}")
        

def insert_game(file, game):
    # Implementar inserção de novo jogo
    pass

def remove_game(file, identifier):
    # Implementar remoção de jogo
    pass

def print_led(file):
    # Implementar impressão da LED
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