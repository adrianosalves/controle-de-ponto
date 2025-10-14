# utils/formatacao.py

from datetime import datetime

def formatar_data_brasil(data_str: str | None, incluir_hora: bool = False) -> str:
    """
    Converte '2025-01-11 12:00:00' → '11/01/2025' (ou '11/01/2025 12:00' se incluir_hora=True)
    """
    if not data_str:
        return "—"
    try:
        # Aceita formatos com ou sem hora
        if len(data_str) > 10:
            dt = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
        else:
            dt = datetime.strptime(data_str, "%Y-%m-%d")
        
        if incluir_hora:
            return dt.strftime("%d/%m/%Y %H:%M")
        else:
            return dt.strftime("%d/%m/%Y")
    except Exception:
        return "—"