import json
from datetime import datetime, timedelta
import investpy
import pandas as pd


def main():
    today = datetime.utcnow().strftime("%d/%m/%Y")
    tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%d/%m/%Y")

    data = investpy.news.economic_calendar(
        from_date=today,
        to_date=tomorrow,
        importances=['high', 'medium'],
        countries=None,
    )

    df = pd.DataFrame(data)
    eventos = []

    for _, row in df.iterrows():

        # Formatando data
        date = datetime.strptime(row['date'], "%d/%m/%Y").strftime("%Y-%m-%d")
        if date != datetime.utcnow().strftime("%Y-%m-%d"):
            continue

        # Hora
        hora = row.get("time", "—")
        if not hora or "all" in str(hora).lower():
            hora = "00:00"

        # Impacto com proteção
        importancia = row.get("importance")
        impacto = importancia.lower() if importancia else "low"

        if impacto not in ("high", "medium"):
            continue

        eventos.append({
            "date": date,
            "time": hora,
            "country": row.get("currency", ""),
            "impact": impacto,
            "title": row.get("event", "Sem título"),
            "previous": row.get("previous", "N/D"),
            "forecast": row.get("forecast", "N/D"),
            "actual": row.get("actual", "N/D")
        })

    # Gravando no formato do bot
    with open("today.json", "w", encoding="utf-8") as f:
        json.dump(eventos, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
