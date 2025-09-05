# ========================== IMPORTANDO BIBLIOTECAS ========================== 
#importando dependencias do Tkinter
from tkinter.ttk import *
from tkinter import*
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog as fd

from PIL import ImageTk, Image #importando pillow

#tk calendar
from tkcalendar import Calendar, DateEntry
from datetime import date
from datetime import datetime

from bd import * # importando o banco de dados

cor1 = "#feffff"  # Branca   
cor2 = "#403d3d"   # letra
cor3 = "#1E90FF"   # cor da logo
cor4 = "#0A1B41"   # azul escuro; fundo dos botões e la na frame logo

DEFAULT_IMG_PATH = 'imagens/logo.png'

# garantem que existem desde o início
imagem_string = ''   # caminho da imagem selecionada (vazio até o usuário escolher)
imagem = None
label_imagem = None

# ========================== FUNÇÕES HELPERS ========================== 
def carregar_imagem(caminho: str):
    """Abre a imagem, redimensiona e atualiza o label, mantendo a referência."""
    global label_imagem, imagem, imagem_string
    try:
        img = Image.open(caminho)
        img = img.resize((130, 130))
        foto = ImageTk.PhotoImage(img)

        if label_imagem is None:
            # cria uma vez
            label_imagem_local = Label(frame_detalhes, image=foto, bg=cor1, fg=cor2)
            label_imagem_local.place(x=390, y=10)
            # guarde referência global
            globals()['label_imagem'] = label_imagem_local
        else:
            label_imagem.configure(image=foto)

        label_imagem.image = foto  # mantém referência
        imagem_string = caminho
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível carregar a imagem:\n{e}")

def carregar_imagem_padrao():
    carregar_imagem(DEFAULT_IMG_PATH)

def limpar_campos():
    entrada_nome.delete(0, END)
    entrada_email.delete(0, END)
    entrada_telefone.delete(0, END)
    combobox_sexo.set('')              # use set em combobox
    try:
        data_nascimento.set_date(date.today())
    except Exception:
        pass
    entrada_endereco.delete(0, END)
    combobox_curso.set('')


# ========================== FUNÇÕES PARA O CRUD ========================== 
def adicionar():
    global imagem_string

    nome = entrada_nome.get().strip()
    email = entrada_email.get().strip()
    telefone = entrada_telefone.get().strip()
    sexo = combobox_sexo.get().strip()
    data_str = data_nascimento.get().strip()  # DateEntry já retorna str com seu pattern
    endereco = entrada_endereco.get().strip()
    curso = combobox_curso.get().strip()
    img = imagem_string  # já existe (inicializamos no topo)

    campos_obrigatorios = [nome, email, telefone, sexo, data_str, endereco, curso, img]
    if any(c == '' for c in campos_obrigatorios):
        messagebox.showerror("Erro", "Preencha todos os campos (incluindo a foto).")
        return

    # (Opcional) validar data:
    try:
        datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        messagebox.showerror("Erro", "Data inválida. Use o formato dd/mm/aaaa.")
        return

    sistema_de_registro.registrar_estudante([nome, email, telefone, sexo, data_str, endereco, curso, img])
    limpar_campos()
    carregar_imagem_padrao()
    mostrar_alunos()

def procurar():
    texto_id = entrada_procurar.get().strip()
    if not texto_id.isdigit():
        messagebox.showerror("Erro", "Digite um ID numérico válido.")
        return

    id_aluno = int(texto_id)
    dados = sistema_de_registro.pesquisar_estudante(id_aluno)

    if not dados:
        messagebox.showinfo("Aviso", f"Nenhum aluno encontrado com ID {id_aluno}.")
        limpar_campos()
        carregar_imagem_padrao()
        return

    # Preenche os campos
    limpar_campos()
    entrada_nome.insert(END, dados[1])
    entrada_email.insert(END, dados[2])
    entrada_telefone.insert(END, dados[3])
    combobox_sexo.set(dados[4])

    try:
        data_nascimento.set_date(dados[5])
    except Exception:
        # Se o banco tiver salvo num outro formato, tente ajustar aqui
        try:
            data_nascimento.set_date(datetime.strptime(dados[5], "%Y-%m-%d").date())
        except Exception:
            data_nascimento.set_date(date.today())

    entrada_endereco.insert(END, dados[6])
    combobox_curso.set(dados[7])

    # Imagem
    caminho_img = dados[8] or DEFAULT_IMG_PATH
    carregar_imagem(caminho_img)

def atualizar():
    global imagem_string
    texto_id = entrada_procurar.get().strip()

    if not texto_id.isdigit():
        messagebox.showerror("Erro", "Digite um ID numérico válido para atualizar.")
        return
    
    id_aluno = int(texto_id)

    #obtendo os valores
    nome = entrada_nome.get()
    email = entrada_email.get()
    telefone = entrada_telefone.get()
    sexo = combobox_sexo.get()
    data = data_nascimento.get()
    endereco = entrada_endereco.get()
    curso = combobox_curso.get()
    img = imagem_string

    lista = [nome, email, telefone, sexo, data, endereco, curso, img, id_aluno]

    # verificando se a lista estar vazia
    for i in lista: 
        if i =='':
            messagebox.showerror("Erro","Preencha todos os campos")
            return
        
    # registrando os valores
    sistema_de_registro.update_estudante(lista)

    # limpando os campos de entradas
    entrada_nome.delete(0, END)
    entrada_email.delete(0, END)
    entrada_telefone.delete(0, END)
    combobox_sexo.delete(0, END)
    data_nascimento.delete(0, END)
    entrada_endereco.delete(0, END)
    combobox_curso.delete(0, END)

    # abrindo a imagem
    imagem = Image.open('imagens/logo.png')
    imagem = imagem.resize((130,130))
    imagem = ImageTk.PhotoImage(imagem)

    label_imagem = Label(frame_detalhes, image=imagem, bg=cor1, fg=cor2)
    label_imagem.place(x=390, y=10)

    # mostrando os valores da tabela
    mostrar_alunos()

def deletar():
    texto_id = entrada_procurar.get().strip()
    if not texto_id.isdigit():
        messagebox.showerror("Erro", "Digite um ID numérico válido para deletar.")
        return
    id_aluno = int(texto_id)

    # Confirmação (opcional)
    if not messagebox.askyesno("Confirmar", f"Deletar aluno ID {id_aluno}?"):
        return

    sistema_de_registro.delete_estudante(id_aluno)
    limpar_campos()
    entrada_procurar.delete(0, END)
    carregar_imagem_padrao()
    mostrar_alunos()

# ========================== FUNÇÕES ========================== 
def escolher_imagem():
    global imagem_string
    caminho = fd.askopenfilename()

    if not caminho:
        return
    
    carregar_imagem(caminho)
    botao_carregar['text'] = 'Trocar de foto'

# declare no topo do arquivo:
tree_aluno = None

def mostrar_alunos():
    global tree_aluno
    list_header = ['id','Nome','email','Telefone','sexo','Data','Endereço','Curso']
    df_list = sistema_de_registro.view_all_students()

    if tree_aluno is None:
        tree_aluno = ttk.Treeview(frame_tabela, selectmode="extended", columns=list_header, show="headings")

        vsb = ttk.Scrollbar(frame_tabela, orient="vertical", command=tree_aluno.yview)
        hsb = ttk.Scrollbar(frame_tabela, orient="horizontal", command=tree_aluno.xview)
        tree_aluno.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree_aluno.grid(column=0, row=1, sticky="nsew")
        vsb.grid(column=1, row=1, sticky='ns')
        hsb.grid(column=0, row=2, sticky='ew')
        frame_tabela.grid_rowconfigure(0, weight=12)

        hd = ["nw","nw","center","center","center","center","center","center"]
        h = [20,130,150,90,35,70,150,150]
        for n, col in enumerate(list_header):
            tree_aluno.heading(col, text=col.title(), anchor=NW)
            tree_aluno.column(col, width=h[n], anchor=hd[n])

    # limpa e repopula
    for item in tree_aluno.get_children():
        tree_aluno.delete(item)

    for row in df_list:
        tree_aluno.insert('', 'end', values=row)
    
# ========================== CRIANDO JANELA ========================== 
janela = Tk()
janela.title("")
janela.geometry('810x535')
janela.configure(background=cor1)
janela.resizable(width=FALSE, height=FALSE)

style = Style(janela)
style.theme_use("clam")

# ========================== FRAMES ========================== 
frame_logo = Frame(janela, width=850, height=52, bg=cor4)
frame_logo.grid(row=0, column=0, pady=0, padx=0, sticky=NSEW, columnspan=5)

frame_botoes = Frame(janela, width=100, height=200, bg=cor1, relief=RAISED)
frame_botoes.grid(row=1, column=0, pady=1, padx=0, sticky=NSEW)

frame_detalhes = Frame(janela, width=800, height=100, bg=cor1, relief=SOLID)
frame_detalhes.grid(row=1, column=1, pady=1, padx=10, sticky=NSEW)

frame_tabela = Frame(janela, width=800, height=100, bg=cor1, relief=SOLID)
frame_tabela.grid(row=3, column=0, pady=0, padx=10, sticky=NSEW, columnspan=5)

# ========================== FRAME LOGO ========================== 
global  l_imagem

app_logo = Image.open('imagens/logo.png')
app_logo = app_logo.resize((50,50)) # alterando o tamanho da imagem
app_logo = ImageTk.PhotoImage(app_logo)
app_logo_label = Label(frame_logo, image=app_logo, text=" Sistema de Registro de Alunos", width=850, compound=LEFT, anchor=NW, font=('Verdana 15'), bg=cor4, fg=cor3)
app_logo_label.place(x=5, y=0)

#abrindo a imagem
imagem = Image.open('imagens/logo.png')
imagem = imagem.resize((130,130)) # alterando o tamanho da imagem
imagem = ImageTk.PhotoImage(imagem)
label_imagem = Label(frame_detalhes, image=imagem, bg=cor1, fg=cor2)
label_imagem.place(x=390, y=10)

# ========================== CAMPOS DE ENTRADA ========================== 
# entrada do nome
label_nome = Label(frame_detalhes, text="Nome *", anchor=NW, font=('Ivy 10'), bg=cor1,fg=cor2)
label_nome.place(x=4, y=10)
entrada_nome = Entry(frame_detalhes, width=30, justify='left', relief='solid')
entrada_nome.place(x=7, y=40)

# entrada do email
label_email = Label(frame_detalhes, text="Email *", anchor=NW, font=('Ivy 10'), bg=cor1,fg=cor2)
label_email.place(x=4, y=70)
entrada_email = Entry(frame_detalhes, width=30, justify='left', relief='solid')
entrada_email.place(x=7, y=100)

# entrada do telefone
label_telefone = Label(frame_detalhes, text="Telefone *", anchor=NW, font=('Ivy 10'), bg=cor1,fg=cor2)
label_telefone.place(x=4, y=130)
entrada_telefone = Entry(frame_detalhes, width=15, justify='left', relief='solid')
entrada_telefone.place(x=7, y=160)

# entrada do sexo
label_sexo = Label(frame_detalhes, text="Sexo *", anchor=NW, font=('Ivy 10'), bg=cor1,fg=cor2)
label_sexo.place(x=127, y=130)
combobox_sexo = ttk.Combobox(frame_detalhes, width=7, font=('Ivy 8 bold'), justify='center')
combobox_sexo['values'] = ('M','F')
combobox_sexo.place(x=130, y=160)

# entrada do data_nascimento
label_data_nascimento = Label(frame_detalhes, text="Data de nascimento *", anchor=NW, font=('Ivy 10'), bg=cor1,fg=cor2)
label_data_nascimento.place(x=220, y=10)
data_nascimento = DateEntry(frame_detalhes, width=18, justify='center', background=cor4, foreground=cor3, borderwidth=2, year=2000, mindate=date(1900,1,1),maxdate=date(2100,12,31),date_pattern='dd/mm/yyyy',locale='pt_BR')
data_nascimento.place(x=224, y=40)

# entrada do endereco
label_endereco = Label(frame_detalhes, text="Endereço *", anchor=NW, font=('Ivy 10'), bg=cor1,fg=cor2)
label_endereco.place(x=220, y=70)
entrada_endereco = Entry(frame_detalhes, width=22, justify='left', relief='solid')
entrada_endereco.place(x=224, y=100)

# entrada do curso
cursos = ["Engenharia de Computação","Ciência da Computação","Engenharia de Software","Sistemas de Informação","Redes de Computadores"]
label_curso = Label(frame_detalhes, text="Cursos *", anchor=NW, font=('Ivy 10'), bg=cor1,fg=cor2)
label_curso.place(x=220, y=130)
combobox_curso = ttk.Combobox(frame_detalhes, width=22, font=('Ivy 8 bold'), justify='center')
combobox_curso['values'] = (cursos)
combobox_curso.place(x=224, y=160)

# ========================== BOTÃO CARREGAR ========================== 
botao_carregar = Button(frame_detalhes, command=escolher_imagem, text='Carregar Foto'.upper(), width=20, compound=CENTER, anchor=CENTER, overrelief=RIDGE, font=('Ivy 7 bold'), bg=cor4, fg=cor1)
botao_carregar.place(x=390, y=160)

# ========================== PROCURAR ALUNO ========================== 
frame_procurar = Frame(frame_botoes, width=40, height=55, bg=cor1, relief=RAISED)
frame_procurar.grid(row=0, column=0, pady=10, padx=10, sticky=NSEW)

label_nome = Label(frame_procurar, text=" Procurar aluno [Entra ID]", anchor=NW, font=('Ivy 10'), bg=cor1,fg=cor2)
label_nome.grid(row=0, column=0, pady=10, padx=0, sticky=NSEW)

entrada_procurar = Entry(frame_procurar, width=5, justify='center', relief='solid', font=('Ivy 10'))
entrada_procurar.grid(row=1, column=0, pady=10, padx=0, sticky=NSEW)

botao_procurar = Button(frame_procurar,text='Procurar',command=procurar, width=9, anchor=CENTER, overrelief=RIDGE, font=('Ivy 7 bold'), bg=cor4, fg=cor1)
botao_procurar.grid(row=1, column=1, pady=10, padx=0, sticky=NSEW)

# ========================== BOTÕES ========================== 
# adicionar
app_img_adicionar = Image.open('imagens/adicionar.png')
app_img_adicionar = app_img_adicionar.resize((25,25))
app_img_adicionar = ImageTk.PhotoImage(app_img_adicionar)

app_adicionar = Button(frame_botoes,image=app_img_adicionar,command=adicionar,relief=GROOVE,text=' Adicionar', width=100,compound=LEFT, overrelief=RIDGE, font=('Ivy 11'), bg=cor4, fg=cor1)
app_adicionar.grid(row=1, column=0, pady=5, padx=10, sticky=NSEW)

# atualizar
app_img_atualizar = Image.open('imagens/atualizar.png')
app_img_atualizar = app_img_atualizar.resize((25,25))
app_img_atualizar = ImageTk.PhotoImage(app_img_atualizar)

app_atualizar = Button(frame_botoes,image=app_img_atualizar,command=atualizar,relief=GROOVE,text=' Atualizar', width=100,compound=LEFT, overrelief=RIDGE, font=('Ivy 11'), bg=cor4, fg=cor1)
app_atualizar.grid(row=2, column=0, pady=5, padx=10, sticky=NSEW)

#deletar
app_img_deletar = Image.open('imagens/deletar.png')
app_img_deletar = app_img_deletar.resize((25,25))
app_img_deletar = ImageTk.PhotoImage(app_img_deletar)

app_deletar = Button(frame_botoes,command=deletar,image=app_img_deletar,relief=GROOVE,text=' Deletar', width=100,compound=LEFT, overrelief=RIDGE, font=('Ivy 11'), bg=cor4, fg=cor1)
app_deletar.grid(row=3, column=0, pady=5, padx=10, sticky=NSEW)

# ========================== LINHA SEPARATORIA ========================== 
app_linha = Button(frame_botoes, relief=GROOVE,text=' h', width=1, height=123, anchor=NW, font=('Ivy 1'), bg=cor1, fg=cor1)
app_linha.place(x=236, y=15)

mostrar_alunos() # chamar tabela
 
janela.mainloop() # abri a janela
