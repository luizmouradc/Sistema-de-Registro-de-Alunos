from pathlib import Path
 
APP_NAME = "Gestão Acadêmica"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PHOTOS_DIR = DATA_DIR / "fotos"
DB_PATH = DATA_DIR / "estudantes.db"
LEGACY_DB_PATH = BASE_DIR / "estudantes.db"
 
CURSOS_PADRAO = [
    "Engenharia de Computação",
    "Ciência da Computação",
    "Engenharia de Software",
    "Sistemas de Informação",
    "Redes de Computadores",
]
 
STATUS_ALUNO = ["Ativo", "Trancado", "Formado", "Inativo"]
SEXOS = ["Masculino", "Feminino", "Outro", "Prefiro não informar"]
 
# Paleta principal
NAVY = "#111827"
NAVY_2 = "#1F2937"
INDIGO = "#4F46E5"
INDIGO_DARK = "#4338CA"
INDIGO_SOFT = "#EEF2FF"
TEXT = "#111827"
TEXT_MUTED = "#6B7280"
BORDER = "#E5E7EB"
BACKGROUND = "#F6F7FB"
SURFACE = "#FFFFFF"
SUCCESS = "#16A34A"
SUCCESS_SOFT = "#DCFCE7"
WARNING = "#D97706"
WARNING_SOFT = "#FEF3C7"
DANGER = "#DC2626"
DANGER_SOFT = "#FEE2E2"
INFO = "#2563EB"
INFO_SOFT = "#DBEAFE"
