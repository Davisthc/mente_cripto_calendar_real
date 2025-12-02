import json
from datetime import datetime, timedelta
import investpy
import pandas as pd

# Palavras que aumentam o peso do evento
IMPORTANT_KEYWORDS = {
    "cpi": 20,
    "core cpi": 25,
    "inflation": 20,
    "interest rate": 25,
    "rate decision": 25,
    "fomc": 30,
    "powell": 30,
    "ecb press conference": 25,
    "lagarde": 25,
    "gdp": 20,
    "gross domestic product": 20,
    "nonfarm": 25,
    "payroll": 25,
    "unemployment rate": 20,
    "jobs report": 20,
    "pmi": 15,
    "manufacturing pmi": 15,
    "services pmi": 15,
    "retail sales": 15,
}

# Coisas que normalmente são "lixo" intraday (CFTC, etc.)
LOW_VALUE_KEYWORDS = [
    "cftc",
    "speculative net positions",
]

# Moedas principais (ganham um pouco mais de score)
BIG_FX = {
    "USD", "EUR", "GBP", "JPY",
    "AUD", "NZD", "CAD", "CHF",
    "CNY", "CNH", "BRL", "ZAR"
}


def score_event(row: pd.Series) -> int:
    """Calcula um score 0–100 para o evento."""

    importance = (row.get("importance") or "").lower()

    # Base pelo importance do Investing
    if importance == "high":
        base = 85
    elif importance == "medium":
        base = 60
    else:
        base = 30

    title = (row.get("event") or "").lower()
    score = base

    # Bônus por palavras importantes
    for kw, bonus in IMPORTANT_KEYWORDS.items():
        if kw in title:
            score += bonus

    # Penalização por eventos fracos
    for kw in LOW_VALUE_KEYWORDS:
        if kw in title:
            score -= 30

    # País/moeda pequena perde um pouco de peso
    currency = (row.get("currency") or "").upper()
    if currency and currency not in BIG_FX:
        score -= 10

    # Limita entre 0 e 100
    return max(0, min(100, score))


def impact_from_score(score: int) -> str:
    """Converte o score em impacto: high / medium / low."""
    if score >= 80:
        return "high"
    elif score >= 50:
        return "medium"
    return "low"


def main():
    # Hoje e amanhã (a API exige intervalo from < to)
    today_dt = datetime.utcnow()
    tomorrow_dt = today_dt + timedelta(days=1)

    today_str = today_dt.strftime("%d/%m/%Y")
    tomorrow_str = tomorrow_dt.strftime("%d/%m/%Y")

    data = investpy.news.economic_calendar(
        from_date=today_str,
        to_date=tomorrow_str,
        countries=None,
        importances=["high", "medium", "low"],  # pegamos tudo, filtramos depois
    )

    df = pd.DataFrame(data)

    eventos = []
    today_iso = today_dt.strftime("%Y-%m-%d")

    for _, row in df.iterrows():
        # Data em YYYY-MM-DD
        try:
            date_iso = datetime.strptime(row["date"], "%d/%m/%Y").strftime("%Y-%m-%d")
        except Exception:
            continue

        # Mantém só o dia de hoje na gravação final
        if date_iso != today_iso:
            continue

        # Hora
        hora = row.get("time") or "00:00"
        hora_str = str(hora)
        if "all" in hora_str.lower():
            hora_str = "00:00"

        # Score e impacto
        s = score_event(row)
        impact = impact_from_score(s)

        eventos.append({
            "date": date_iso,
            "time": hora_str,
            "country": (row.get("currency") or "").upper(),
            "title": row.get("event") or "Sem título",
            "previous": row.get("previous") or "N/D",
            "forecast": row.get("forecast") or "N/D",
            "actual": row.get("actual") or "N/D",
            "raw_importance": (row.get("importance") or "").lower(),
            "score": s,
            "impact": impact,
        })

    # Ordena por horário
    def sort_key(e):
        try:
            return datetime.strptime(e["time"], "%H:%M").time()
        except Exception:
            return datetime.min.time()

    eventos.sort(key=sort_key)

    # Salva no formato que o bot usa
    with open("today.json", "w", encoding="utf-8") as f:
        json.dump(eventos, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
