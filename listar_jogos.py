import struct

class Game:
    def __init__(self, identifier, title, year, genre, producer, platform):
        self.identifier = identifier
        self.title = title
        self.year = year
        self.genre = genre
        self.producer = producer
        self.platform = platform

    def __str__(self):
        return f"{self.identifier}|{self.title}|{self.year}|{self.genre}|{self.producer}|{self.platform}"

def read_game(file, offset):
    file.seek(offset)
    tamanho_registro_bytes = file.read(2)
    if not tamanho_registro_bytes:
        return None
    
    tamanho_registro = struct.unpack('<H', tamanho_registro_bytes)[0]
    record_data = file.read(tamanho_registro)
    parts = record_data.split(b'|')

    if len(parts) < 6:
        print(f"Registro inválido no offset {offset}: {record_data}")
        return None

    try:
        identifier = parts[0].decode('utf-8').strip()
        title = parts[1].decode('utf-8').strip()
        year = int(parts[2].decode('utf-8').strip())
        genre = parts[3].decode('utf-8').strip()
        producer = parts[4].decode('utf-8').strip()
        platform = parts[5].decode('utf-8').strip()
    except UnicodeDecodeError as e:
        print(f"Erro de decodificação no offset {offset}: {e}")
        return None
    except ValueError as e:
        print(f"Erro de valor no offset {offset}: {e}")
        return Game(identifier, title, 0, "Unknown", "Unknown", "Unknown")

    return Game(identifier, title, year, genre, producer, platform)

def list_all_games(file):
    offset = 4  # Ignora os primeiros 4 bytes iniciais
    tamanho_maximo_registro = 264

    while True:
        game = read_game(file, offset)
        if game is None:
            break

        print(game)
        offset += tamanho_maximo_registro

def main():
    try:
        with open('dados.dat', 'rb') as file:
            list_all_games(file)
    except FileNotFoundError:
        print("Erro: arquivo dados.dat não encontrado.")

if __name__ == "__main__":
    main()
