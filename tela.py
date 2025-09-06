# ========================== IMPORTS ==========================
from pathlib import Path
import re
from datetime import date, datetime

import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk

from PIL import Image, ImageTk
from tkcalendar import DateEntry

from bd import sistema_de_registro  # instancia já criada no seu bd.py

# ========================== CONSTANTES =======================
COR_BG = "#feffff"   # branca
COR_TXT = "#403d3d"  # texto
COR_LOGO = "#1E90FF" # cor da logo
COR_AZUL = "#0A1B41" # azul escuro (fundo dos botões e barra)

IMAGENS_DIR = Path("imagens")
DEFAULT_IMG_PATH = IMAGENS_DIR / "logo.png"

CURSOS = [
    "Engenharia de Computação",
    "Ciência da Computação",
    "Engenharia de Software",
    "Sistemas de Informação",
    "Redes de Computadores",
]

# ========================== HELPERS ==========================
def is_email(val: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", val))

def is_phone(val: str) -> bool:
    # simples: 8–15 dígitos (permite DDD). Ajuste se quiser máscara.
    return bool(re.fullmatch(r"\d{8,15}", val))

def parse_data_br(data_str: str) -> datetime | None:
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except Exception:
        return None


# ========================== APP ==============================
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sistema de Registro de Alunos")
        self.root.geometry("810x535")
        self.root.configure(background=COR_BG)
        self.root.resizable(False, False)

        # ttk theme
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # estado
        self.imagem_path: Path | None = None
        self.photo_ref: ImageTk.PhotoImage | None = None
        self.tree: ttk.Treeview | None = None

        # frames
        self._build_frames()
        self._build_logo_area()
        self._build_form()
        self._build_search()
        self._build_buttons()
        self._build_table()

        self._carregar_imagem(DEFAULT_IMG_PATH)
        self._mostrar_alunos()

    # ----------------------- UI BUILDERS ----------------------
    def _build_frames(self):
        self.frame_logo = tk.Frame(self.root, width=850, height=52, bg=COR_AZUL)
        self.frame_logo.grid(row=0, column=0, pady=0, padx=0, sticky="nsew", columnspan=5)

        self.frame_botoes = tk.Frame(self.root, width=100, height=200, bg=COR_BG, relief=tk.RAISED)
        self.frame_botoes.grid(row=1, column=0, pady=1, padx=0, sticky="nsew")

        self.frame_detalhes = tk.Frame(self.root, width=800, height=100, bg=COR_BG, relief=tk.SOLID)
        self.frame_detalhes.grid(row=1, column=1, pady=1, padx=10, sticky="nsew")

        self.frame_tabela = tk.Frame(self.root, width=800, height=100, bg=COR_BG, relief=tk.SOLID)
        self.frame_tabela.grid(row=3, column=0, pady=0, padx=10, sticky="nsew", columnspan=5)

    def _build_logo_area(self):
        # logo pequena + título
        try:
            img = Image.open(DEFAULT_IMG_PATH).resize((50, 50))
            logo = ImageTk.PhotoImage(img)
        except Exception:
            logo = None

        lbl = tk.Label(
            self.frame_logo,
            image=logo,
            text=" Sistema de Registro de Alunos",
            width=850,
            compound=tk.LEFT,
            anchor="nw",
            font=("Verdana", 15),
            bg=COR_AZUL,
            fg=COR_LOGO,
        )
        lbl.image = logo
        lbl.place(x=5, y=0)

    def _build_form(self):
        # imagem grande
        self.lbl_imagem = tk.Label(self.frame_detalhes, bg=COR_BG, fg=COR_TXT)
        self.lbl_imagem.place(x=390, y=10, width=130, height=130)

        # Nome
        tk.Label(self.frame_detalhes, text="Nome *", anchor="nw",
                 font=("Ivy", 10), bg=COR_BG, fg=COR_TXT).place(x=4, y=10)
        self.ent_nome = tk.Entry(self.frame_detalhes, width=30, justify="left", relief="solid")
        self.ent_nome.place(x=7, y=40)

        # Email
        tk.Label(self.frame_detalhes, text="Email *", anchor="nw",
                 font=("Ivy", 10), bg=COR_BG, fg=COR_TXT).place(x=4, y=70)
        self.ent_email = tk.Entry(self.frame_detalhes, width=30, justify="left", relief="solid")
        self.ent_email.place(x=7, y=100)

        # Telefone
        tk.Label(self.frame_detalhes, text="Telefone *", anchor="nw",
                 font=("Ivy", 10), bg=COR_BG, fg=COR_TXT).place(x=4, y=130)
        self.ent_tel = tk.Entry(self.frame_detalhes, width=15, justify="left", relief="solid")
        self.ent_tel.place(x=7, y=160)

        # Sexo
        tk.Label(self.frame_detalhes, text="Sexo *", anchor="nw",
                 font=("Ivy", 10), bg=COR_BG, fg=COR_TXT).place(x=127, y=130)
        self.cb_sexo = ttk.Combobox(self.frame_detalhes, width=7, font=("Ivy", 8, "bold"), justify="center",
                                    values=("M", "F"), state="readonly")
        self.cb_sexo.place(x=130, y=160)

        # Data nasc
        tk.Label(self.frame_detalhes, text="Data de nascimento *", anchor="nw",
                 font=("Ivy", 10), bg=COR_BG, fg=COR_TXT).place(x=220, y=10)
        self.dt_nasc = DateEntry(
            self.frame_detalhes, width=18, justify="center",
            background=COR_AZUL, foreground=COR_LOGO, borderwidth=2,
            year=2000, mindate=date(1900, 1, 1), maxdate=date(2100, 12, 31),
            date_pattern="dd/mm/yyyy", locale="pt_BR"
        )
        self.dt_nasc.place(x=224, y=40)

        # Endereço
        tk.Label(self.frame_detalhes, text="Endereço *", anchor="nw",
                 font=("Ivy", 10), bg=COR_BG, fg=COR_TXT).place(x=220, y=70)
        self.ent_end = tk.Entry(self.frame_detalhes, width=22, justify="left", relief="solid")
        self.ent_end.place(x=224, y=100)

        # Curso
        tk.Label(self.frame_detalhes, text="Cursos *", anchor="nw",
                 font=("Ivy", 10), bg=COR_BG, fg=COR_TXT).place(x=220, y=130)
        self.cb_curso = ttk.Combobox(self.frame_detalhes, width=22, font=("Ivy", 8, "bold"),
                                     justify="center", values=CURSOS, state="readonly")
        self.cb_curso.place(x=224, y=160)

        # Botão carregar imagem
        self.btn_carregar = tk.Button(
            self.frame_detalhes, command=self._escolher_imagem,
            text="CARREGAR FOTO", width=20, compound="center", anchor="center",
            overrelief="ridge", font=("Ivy", 7, "bold"), bg=COR_AZUL, fg=COR_BG
        )
        self.btn_carregar.place(x=390, y=160)

    def _build_search(self):
        frame = tk.Frame(self.frame_botoes, width=40, height=55, bg=COR_BG, relief=tk.RAISED)
        frame.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        tk.Label(frame, text=" Procurar aluno [Entre ID]", anchor="nw",
                 font=("Ivy", 10), bg=COR_BG, fg=COR_TXT).grid(row=0, column=0, pady=10, padx=0, sticky="nsew")

        self.ent_busca = tk.Entry(frame, width=5, justify="center", relief="solid", font=("Ivy", 10))
        self.ent_busca.grid(row=1, column=0, pady=10, padx=0, sticky="nsew")

        tk.Button(frame, text="Procurar", command=self._procurar, width=9, anchor="center",
                  overrelief="ridge", font=("Ivy", 7, "bold"), bg=COR_AZUL, fg=COR_BG).grid(
            row=1, column=1, pady=10, padx=5, sticky="nsew"
        )

        # divisor visual
        tk.Label(self.frame_botoes, text=" ", width=1, height=8,
                 bg=COR_BG, fg=COR_BG).place(x=236, y=15)

    def _build_buttons(self):
        # Adicionar
        add_img = self._load_icon("adicionar.png")
        tk.Button(
            self.frame_botoes, image=add_img, command=self._adicionar,
            relief="groove", text=" Adicionar", width=100, compound="left",
            overrelief="ridge", font=("Ivy", 11), bg=COR_AZUL, fg=COR_BG
        ).grid(row=1, column=0, pady=5, padx=10, sticky="nsew")

        # Atualizar
        upd_img = self._load_icon("atualizar.png")
        tk.Button(
            self.frame_botoes, image=upd_img, command=self._atualizar,
            relief="groove", text=" Atualizar", width=100, compound="left",
            overrelief="ridge", font=("Ivy", 11), bg=COR_AZUL, fg=COR_BG
        ).grid(row=2, column=0, pady=5, padx=10, sticky="nsew")

        # Deletar
        del_img = self._load_icon("deletar.png")
        tk.Button(
            self.frame_botoes, image=del_img, command=self._deletar,
            relief="groove", text=" Deletar", width=100, compound="left",
            overrelief="ridge", font=("Ivy", 11), bg=COR_AZUL, fg=COR_BG
        ).grid(row=3, column=0, pady=5, padx=10, sticky="nsew")

        # manter referências dos ícones
        self._icons = (add_img, upd_img, del_img)

    def _build_table(self):
        headers = ["id", "Nome", "email", "Telefone", "sexo", "Data", "Endereço", "Curso"]
        self.tree = ttk.Treeview(self.frame_tabela, selectmode="extended", columns=headers, show="headings")

        vsb = ttk.Scrollbar(self.frame_tabela, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.frame_tabela, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(column=0, row=1, sticky="nsew")
        vsb.grid(column=1, row=1, sticky="ns")
        hsb.grid(column=0, row=2, sticky="ew")
        self.frame_tabela.grid_rowconfigure(0, weight=12)

        anchors = ["nw", "nw", "center", "center", "center", "center", "center", "center"]
        widths = [20, 130, 150, 90, 35, 70, 150, 150]
        for i, col in enumerate(headers):
            self.tree.heading(col, text=col.title(), anchor="nw")
            self.tree.column(col, width=widths[i], anchor=anchors[i])

    def _load_icon(self, name: str) -> ImageTk.PhotoImage | None:
        path = IMAGENS_DIR / name
        try:
            return ImageTk.PhotoImage(Image.open(path).resize((25, 25)))
        except Exception:
            return None

    # ----------------------- IMAGE HANDLING --------------------
    def _carregar_imagem(self, caminho: Path):
        try:
            img = Image.open(caminho).resize((130, 130))
            foto = ImageTk.PhotoImage(img)
            self.lbl_imagem.configure(image=foto)
            self.lbl_imagem.image = foto  # manter referência
            self.photo_ref = foto
            self.imagem_path = caminho
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem:\n{e}")

    def _carregar_imagem_padrao(self):
        self._carregar_imagem(DEFAULT_IMG_PATH)

    def _escolher_imagem(self):
        caminho = filedialog.askopenfilename(
            title="Selecione a foto",
            filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("Todos os arquivos", "*.*")]
        )
        if not caminho:
            return
        self._carregar_imagem(Path(caminho))
        self.btn_carregar["text"] = "TROCAR FOTO"

    # ----------------------- FORM UTILS ------------------------
    def _limpar_campos(self):
        self.ent_nome.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)
        self.ent_tel.delete(0, tk.END)
        self.cb_sexo.set("")
        try:
            self.dt_nasc.set_date(date.today())
        except Exception:
            pass
        self.ent_end.delete(0, tk.END)
        self.cb_curso.set("")
        self._carregar_imagem_padrao()
        self.btn_carregar["text"] = "CARREGAR FOTO"

    def _get_form(self):
        return {
            "nome": self.ent_nome.get().strip(),
            "email": self.ent_email.get().strip(),
            "telefone": self.ent_tel.get().strip(),
            "sexo": self.cb_sexo.get().strip(),
            "data_str": self.dt_nasc.get().strip(),
            "endereco": self.ent_end.get().strip(),
            "curso": self.cb_curso.get().strip(),
            "img": str(self.imagem_path) if self.imagem_path else "",
        }

    def _validar_form(self, dados: dict) -> bool:
        obrigatorios = ["nome", "email", "telefone", "sexo", "data_str", "endereco", "curso", "img"]
        faltando = [k for k in obrigatorios if not dados[k]]
        if faltando:
            messagebox.showerror("Erro", "Preencha todos os campos (incluindo a foto).")
            return False

        if not is_email(dados["email"]):
            messagebox.showerror("Erro", "E-mail inválido.")
            return False

        if not is_phone(dados["telefone"]):
            messagebox.showerror("Erro", "Telefone inválido. Use apenas dígitos (8 a 15).")
            return False

        if not parse_data_br(dados["data_str"]):
            messagebox.showerror("Erro", "Data inválida. Use o formato dd/mm/aaaa.")
            return False

        return True

    # ----------------------- CRUD ------------------------------
    def _adicionar(self):
        dados = self._get_form()
        if not self._validar_form(dados):
            return

        sistema_de_registro.registrar_estudante([
            dados["nome"], dados["email"], dados["telefone"], dados["sexo"],
            dados["data_str"], dados["endereco"], dados["curso"], dados["img"]
        ])
        self._limpar_campos()
        self._mostrar_alunos()

    def _procurar(self):
        texto_id = self.ent_busca.get().strip()
        if not texto_id.isdigit():
            messagebox.showerror("Erro", "Digite um ID numérico válido.")
            return

        aluno = sistema_de_registro.pesquisar_estudante(int(texto_id))
        if not aluno:
            messagebox.showinfo("Aviso", f"Nenhum aluno encontrado com ID {texto_id}.")
            self._limpar_campos()
            return

        # Preenche
        self._limpar_campos()
        self.ent_nome.insert(tk.END, aluno[1])
        self.ent_email.insert(tk.END, aluno[2])
        self.ent_tel.insert(tk.END, aluno[3])
        self.cb_sexo.set(aluno[4])

        # data
        ok = False
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                self.dt_nasc.set_date(datetime.strptime(aluno[5], fmt).date())
                ok = True
                break
            except Exception:
                pass
        if not ok:
            try:
                self.dt_nasc.set_date(date.today())
            except Exception:
                pass

        self.ent_end.insert(tk.END, aluno[6])
        self.cb_curso.set(aluno[7])

        caminho_img = Path(aluno[8]) if aluno[8] else DEFAULT_IMG_PATH
        self._carregar_imagem(caminho_img)

    def _atualizar(self):
        texto_id = self.ent_busca.get().strip()
        if not texto_id.isdigit():
            messagebox.showerror("Erro", "Digite um ID numérico válido para atualizar.")
            return
        dados = self._get_form()
        if not self._validar_form(dados):
            return

        sistema_de_registro.update_estudante([
            dados["nome"], dados["email"], dados["telefone"], dados["sexo"],
            dados["data_str"], dados["endereco"], dados["curso"], dados["img"],
            int(texto_id)
        ])
        self._limpar_campos()
        self.ent_busca.delete(0, tk.END)
        self._mostrar_alunos()

    def _deletar(self):
        texto_id = self.ent_busca.get().strip()
        if not texto_id.isdigit():
            messagebox.showerror("Erro", "Digite um ID numérico válido para deletar.")
            return

        id_aluno = int(texto_id)
        if not messagebox.askyesno("Confirmar", f"Deletar aluno ID {id_aluno}?"):
            return

        sistema_de_registro.delete_estudante(id_aluno)
        self._limpar_campos()
        self.ent_busca.delete(0, tk.END)
        self._mostrar_alunos()

    # ----------------------- TABELA ----------------------------
    def _mostrar_alunos(self):
        assert self.tree is not None
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in sistema_de_registro.view_all_students():
            self.tree.insert("", "end", values=row)


# ========================== MAIN =============================
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
