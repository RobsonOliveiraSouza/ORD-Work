import sys

class Game:
    def __init__(self, identifier, title, year, genre, producer, platform):
        self.identifier = identifier
        self.title = title
        self.year = year
        self.genre = genre
        self.producer = producer
        self.platform = platform

    def to_string(self, tamanho_registro: int) -> str:
        return f'|{self.identifier}|{self.title}|{self.year}|{self.genre}|{self.producer}|{self.platform}| ({tamanho_registro} bytes)'

    
    @classmethod
    def from_bytes(self, data):
        parts = data.split(b'|')
        if len(parts) < 6:
            raise ValueError("Dados incompletos para um jogo")


        identifier = parts[0].decode()
        # identifier = int.from_bytes(parts[0])
        title = parts[1].decode()
        try:
            year = int(parts[2].decode())
        except ValueError:
            year = 0  # Define um valor padrão para o ano inválido

        genre = parts[3].decode()
        producer = parts[4].decode()
        platform = parts[5].decode()

        return self(identifier, title, year, genre, producer, platform)

def leia_reg(file) -> tuple[int, str] | None:
    try:
        bytes_registro = file.read(2) # Lê o tamanho que fica na frente do registro
        if not bytes_registro:
            return None
        tamanho_registro = int.from_bytes(bytes_registro)
        # print(f'Tamanho do registro: {tamanho_registro}')
        if tamanho_registro > 0:
            registro = file.read(tamanho_registro)
            return (tamanho_registro, registro)
        return None
    except Exception as e:
        print(f'Erro leia_reg: {e}')
        return None

def buscar_jogo_por_id(file, identificador) -> tuple[Game, int] | None:
    # PUla os 4 bytes do cabeçalho
    file.seek(4)
    while True:
        tamanho_registro_e_dados = leia_reg(file)
        if not tamanho_registro_e_dados:
            return None
        (tamanho_registro, registro) = tamanho_registro_e_dados
        game = Game.from_bytes(registro)
        # print(f'Id do objeto Game: {game.identifier}. Identificador: {str(identificador)}')
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
    pass

def remove_game(file, identifier):
    pass

def print_led(file):
    pass

def process_operations(file, arquivo_de_operacoes):
    for linha in arquivo_de_operacoes:
        linha_arquivo_operacoes = linha.strip().split(maxsplit=1)
        if not linha_arquivo_operacoes or len(linha_arquivo_operacoes) < 2:
            print(f"Operação inválida ou vazia: {linha}")
            continue

        comando, argumento = (linha_arquivo_operacoes[0], linha_arquivo_operacoes[1]) # [b, 22] OU [i, <registro>] OU [d, 22], por exemplo
        match comando:
            case 'b':
                try:
                    identifier = int(argumento)
                    search_game(file, identifier)
                except ValueError:
                    print(f"Identificador inválido para busca: {argumento}")
            case 'i':
                game_data = argumento.split('|')
                if len(game_data) == 6:
                    try:
                        game = Game(game_data[0], game_data[1], int(game_data[2]), game_data[3], game_data[4], game_data[5])
                        insert_game(file, game)
                    except ValueError as ve:
                        print(f"Erro ao inserir jogo: {ve}")
                else:
                    print(f"Dados incompletos para inserção de jogo: {argumento}")
            case 'r':
                try:
                    identifier = int(argumento)
                    remove_game(file, identifier)
                except ValueError:
                    print(f"Identificador inválido para remoção: {argumento}")
            case _:
                print(f"Operação não reconhecida: {linha}")

def main():
    if len(sys.argv) < 3:
        print("Uso: python programa.py -e arquivo_operacoes")
        return

    mode = sys.argv[1]
    arquivo_operacoes = sys.argv[2]

    try:
        with open('dados.dat', 'r+b') as arquivo_dat:
            if mode == '-e':
                with open(arquivo_operacoes, 'r') as op_file:
                    operacoes = op_file.readlines()
                    process_operations(arquivo_dat, operacoes)
            elif mode == '-p':
                print_led(arquivo_dat)
    except FileNotFoundError:
        print("Erro: arquivo dados.dat não encontrado.")

if __name__ == "__main__":
    main()
