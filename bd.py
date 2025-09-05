import sqlite3
from tkinter import messagebox

class SistemaDeRegistro:
    # permitir fazer a criacaoo do banco de dados
    def __init__(self):
        self.conn = sqlite3.connect('estudantes.db') # db = data base (banco de dados)
        self.c = self.conn.cursor()
        self.create_table() # cria tabelas no banco de dados

    def create_table(self):
        # cria uma tabela chamada "estudantes" se não existir
        # no id ...,cada novo registro recebe um id sequencial sem voce precisar informar
        # TEXT NOT NULL = armazena texto e nao pode ficar vazio
        self.c.execute('''CREATE TABLE IF NOT EXISTS estudantes ( 
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       nome TEXT NOT NULL,
                       email TEXT NOT NULL,
                       telefone TEXT NOT NULL,
                       sexo TEXT NOT NULL,
                       data_nascimento TEXT NOT NULL,
                       endereco TEXT NOT NULL,
                       curso TEXT NOT NULL,
                       picture TEXT NOT NULL)''')

    # metodo para fazer registrar novos alunos
    def registrar_estudante(self, estudantes):
        self.c.execute("INSERT INTO estudantes (nome, email, telefone, sexo, data_nascimento, endereco, curso, picture) VALUES (?,?,?,?,?,?,?,?)", (estudantes))
        self.conn.commit()

        # mostrando menssgem de sucesso
        messagebox.showinfo('Sucesso!', 'Registro com sucesso!')

    # metodo pra ve todas as informacoes dos estudantes
    def view_all_students(self):
        self.c.execute("SELECT * FROM estudantes")
        dados = self.c.fetchall() # retorna todas as informacoes

        return dados

    # metodo de procurar estudante
    def pesquisar_estudante(self, id):
        self.c.execute("SELECT * FROM estudantes WHERE id=?", (id,))
        dados = self.c.fetchone()

        return dados

    # Atualizar os dados dos estudantes
    def update_estudante(self, novo_valores):
        query = "UPDATE estudantes SET nome =?, email=?, telefone=?, sexo=?, data_nascimento=?, endereco=?, curso=?, picture=? WHERE id=? " # variavel que vai ter o comando sql, que vai permitr fazer essa "atualizacao"
        self.c.execute(query, novo_valores)
        self.conn.commit()
        messagebox.showinfo('Sucesso!', f'Estudante com ID:{novo_valores[8]} foi atualizado!')

    # metodo de deletar estudante
    def delete_estudante(self, id):
        self.c.execute("DELETE FROM estudantes WHERE id=?", (id,))
        self.conn.commit()
        messagebox.showinfo('Sucesso!', f'Estudante com ID:{id} foi deletado!')

# criando uma instancia do registro para testar
sistema_de_registro = SistemaDeRegistro()

# -------------- TESTES -------------------
# +++ registrar aluno +++
#estudante = ('fulano', 'email@gmail','1512', 'M','12/85/14102', 'campina grnade', 'computação','imagem.png')
#sistema_de_registro.registrar_estudante(estudante)

# +++ ve os estudantes +++
#todos_alunos = sistema_de_registro.view_all_students()

# +++ pesquisar aluno +++
#aluno = sistema_de_registro.pesquisar_estudante(3)

# +++ atualizar +++
#estudante = ('LUIZ', 'email@gmail','1154879584', 'M','12/85/14102', 'campina grnade', 'MEDICINA','imagem.png', 2)
#atualizar = sistema_de_registro.update_estudante(estudante)

# +++ deletar aluno +++
#sistema_de_registro.delete_estudante(1);
# ----------------------------------------
