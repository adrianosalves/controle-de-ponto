# utils/calculos.py
from datetime import datetime, time, timedelta
import calendar

def is_fim_de_semana(dt: datetime) -> bool:
    """Retorna True se for sábado (5) ou domingo (6)."""
    return dt.weekday() >= 5

def horas_entre(inicio: datetime, fim: datetime, periodo_inicio: time, periodo_fim: time) -> float:
    """
    Calcula horas dentro de um período específico (ex: 21h-24h) entre dois datetimes.
    Suporta intervalos que cruzam dias.
    """
    total_segundos = 0
    current = inicio

    while current < fim:
        # Data do dia atual
        dia = current.date()

        # Definir início e fim do período neste dia
        periodo_start = datetime.combine(dia, periodo_inicio)
        periodo_end = datetime.combine(dia, periodo_fim)

        # Se o período termina à meia-noite, ajustar para 24:00 (próximo dia 00:00)
        if periodo_fim == time(0, 0):
            periodo_end = datetime.combine(dia + timedelta(days=1), time(0, 0))

        # Interseção entre [current, fim] e [periodo_start, periodo_end]
        seg_inicio = max(current, periodo_start)
        seg_fim = min(fim, periodo_end)

        if seg_inicio < seg_fim:
            total_segundos += (seg_fim - seg_inicio).total_seconds()

        # Avança para o próximo dia
        current = datetime.combine(dia + timedelta(days=1), time(0, 0))

    return total_segundos / 3600  # em horas

def calcular_detalhes_horas(entrada: datetime, saida: datetime, inicio_intervalo: datetime = None, fim_intervalo: datetime = None):
    if saida <= entrada:
        return {"erro": "Saída antes da entrada"}

    # Total bruto
    total_bruto_seg = (saida - entrada).total_seconds()
    
    # Descontar intervalo, se válido
    intervalo_seg = 0
    if inicio_intervalo and fim_intervalo and fim_intervalo > inicio_intervalo:
        # Verifica se o intervalo está dentro do expediente
        if entrada <= inicio_intervalo and fim_intervalo <= saida:
            intervalo_seg = (fim_intervalo - inicio_intervalo).total_seconds()
        # Se estiver parcialmente fora, ignora (ou ajusta conforme regra da empresa)

    total_liquido_seg = total_bruto_seg - intervalo_seg
    total_horas = total_liquido_seg / 3600

    # Verifica se é fim de semana
    eh_fds = is_fim_de_semana(entrada) or is_fim_de_semana(saida)

    # Inicializa contadores
    extras_50 = 0.0
    extras_100 = 0.0
    noturnas = 0.0
    adicional_noturno = 0.0

    if eh_fds:
        # Todo o tempo é extra 100%
        extras_100 = total_horas
    else:
        # Dias úteis: só conta como extra 50% após as 17h
        # Calcula quanto tempo está após as 17h
        periodo_extra_inicio = datetime.combine(entrada.date(), time(17, 0))
        if saida > periodo_extra_inicio:
            # Pode haver múltiplos dias? Vamos assumir que não (simplificação)
            # Mas vamos usar a função genérica para segurança
            extras_50 = horas_entre(
                max(entrada, periodo_extra_inicio),
                saida,
                time(17, 0),
                time(23, 59, 59)  # até quase meia-noite
            )
            # Corrige: se cruzar meia-noite, o restante vai para adicional noturno
            # (mas vamos tratar abaixo)

    # Horas noturnas: 21h às 24h
    noturnas = horas_entre(entrada, saida, time(21, 0), time(0, 0))

    # Adicional noturno: 0h às 7h
    adicional_noturno = horas_entre(entrada, saida, time(0, 0), time(7, 0))

    # Ajuste: em dias úteis, o tempo após 17h que cai na madrugada já está em adicional_noturno,
    # mas não deve ser contado duas vezes. Nossa função `horas_entre` já isola os períodos,
    # então está OK.

    # Arredondar para 1 casa decimal
    return {
        "total_horas": round(total_horas, 1),
        "extras_50": round(extras_50, 1),
        "extras_100": round(extras_100, 1),
        "noturnas": round(noturnas, 1),
        "adicional_noturno": round(adicional_noturno, 1),
        "intervalo_horas": round(intervalo_seg / 3600, 1) if intervalo_seg > 0 else 0.0
    }

def formatar_relatorio_horas(entrada_str: str, saida_str: str | None, inicio_intervalo_str: str | None = None, fim_intervalo_str: str | None = None):
    if not saida_str or not entrada_str:
        return {
            "total": "—", "extras_50": "—", "extras_100": "—",
            "noturnas": "—", "adicional_noturno": "—", "intervalo": "—"
        }
    try:
        fmt = "%Y-%m-%d %H:%M:%S"
        entrada = datetime.strptime(entrada_str, fmt)
        saida = datetime.strptime(saida_str, fmt)
        inicio_intervalo = datetime.strptime(inicio_intervalo_str, fmt) if inicio_intervalo_str else None
        fim_intervalo = datetime.strptime(fim_intervalo_str, fmt) if fim_intervalo_str else None
        
        detalhes = calcular_detalhes_horas(entrada, saida, inicio_intervalo, fim_intervalo)
        if "erro" in detalhes:
            return {k: "Erro" for k in ["total", "extras_50", "extras_100", "noturnas", "adicional_noturno", "intervalo"]}
        return {
            "total": f"{detalhes['total_horas']}h",
            "extras_50": f"{detalhes['extras_50']}h",
            "extras_100": f"{detalhes['extras_100']}h",
            "noturnas": f"{detalhes['noturnas']}h",
            "adicional_noturno": f"{detalhes['adicional_noturno']}h",
            "intervalo": f"{detalhes['intervalo_horas']}h" if detalhes['intervalo_horas'] > 0 else "—"
        }
    except Exception:
        return {k: "Erro" for k in ["total", "extras_50", "extras_100", "noturnas", "adicional_noturno", "intervalo"]}
        
# utils/calculos.py (adicione ao final)

def somar_horas_por_registros(registros):
    total_horas = 0.0
    total_extras_50 = 0.0
    total_extras_100 = 0.0
    total_noturnas = 0.0
    total_adicional_noturno = 0.0
    total_intervalo = 0.0
    pendentes = 0

    for r in registros:
        if not r['saida']:
            pendentes += 1
            continue
        try:
            fmt = "%Y-%m-%d %H:%M:%S"
            entrada = datetime.strptime(r['entrada'], fmt)
            saida = datetime.strptime(r['saida'], fmt)
            inicio_intervalo = datetime.strptime(r['inicio_intervalo'], fmt) if r['inicio_intervalo'] else None
            fim_intervalo = datetime.strptime(r['fim_intervalo'], fmt) if r['fim_intervalo'] else None
            
            detalhes = calcular_detalhes_horas(entrada, saida, inicio_intervalo, fim_intervalo)
            if "erro" not in detalhes:
                total_horas += detalhes["total_horas"]
                total_extras_50 += detalhes["extras_50"]
                total_extras_100 += detalhes["extras_100"]
                total_noturnas += detalhes["noturnas"]
                total_adicional_noturno += detalhes["adicional_noturno"]
                total_intervalo += detalhes["intervalo_horas"]
        except Exception:
            continue

    return {
        "total_horas": round(total_horas, 1),
        "extras_50": round(total_extras_50, 1),
        "extras_100": round(total_extras_100, 1),
        "noturnas": round(total_noturnas, 1),
        "adicional_noturno": round(total_adicional_noturno, 1),
        "intervalo_total": round(total_intervalo, 1),
        "pendentes": pendentes
    }