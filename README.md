# Sistema de Registro de Alunos

## Sobre o projeto
O Sistema de Registro de Alunos é uma aplicação desktop desenvolvida em Python com Tkinter para gerenciar informações de estudantes.
Permite cadastrar, atualizar, excluir e pesquisar alunos em um banco de dados SQLite, incluindo foto e dados pessoais.

A interface foi construída para ser simples e intuitiva, facilitando o uso em escolas, cursos ou pequenos sistemas de secretaria.

---

## Funcionalidades da aplicação

### Visão geral das funcionalidades:
1. **Cadastro de Alunos:**
   - Campos obrigatórios: nome, e-mail, telefone, sexo, data de nascimento, endereço, curso e foto.
   - Validação de campos e datas.

2. **Gerenciamento de Registros:**
   - Adicionar novos alunos.
   - Pesquisar por ID.
   - Atualizar dados já cadastrados.
   - Deletar registros com confirmação.

3. **Exibição em Tabela:**
   - Visualização dos alunos em um Treeview (com barra de rolagem horizontal e vertical).
   - Atualização em tempo real após qualquer operação de CRUD.

4. **Gerenciamento de Imagens:**
   - Carregamento de foto personalizada para cada aluno.
   - Imagem padrão exibida caso nenhuma seja selecionada.

5. **Banco de Dados Integrado:**
   - Utilização do SQLite.
   - Criação automática do banco estudantes.db e da tabela estudantes.

---

## Uso

### Pré-requisitos
- Python 3.10+
- Bibliotecas necessárias: ```pip install Pillow tkcalendar```

### Execução
1. Certifique-se de que a pasta ```imagens/``` contém os arquivos:
   - ```logo.png```
   - ```adicionar.png```
   - ```atualizar.png```
   - ```deletar.png```
2. Execute o comando: ```python app.py```

---

## Visualização
Exemplo da tela principal do sistema em funcionamento:

<p align="center">
  <img width="705" height="463" alt="Sistema de Registro de Alunos - Tela principal" src="https://github.com/user-attachments/assets/4c95ea9a-19fd-411f-b030-c65cf2cd54ae" />
</p>


---

## Estrutura de arquivos

  ```
.
├─ app.py        # Interface Tkinter e lógica principal
├─ bd.py         # Classe SistemaDeRegistro (CRUD em SQLite)
├─ estudantes.db # Banco de dados (gerado automaticamente)
├─ imagens/
│  ├─ logo.png
│  ├─ adicionar.png
│  ├─ atualizar.png
│  └─ deletar.png
└─ README.md

  ```

---

## Ferramentas utilizadas

- Python 3.10+
- Tkinter (GUI)
- SQLite3 (banco de dados local)
- Pillow (manipulação de imagens)
- tkcalendar (seleção de datas)
- VSCode (editor de código)
