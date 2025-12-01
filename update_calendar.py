import json
from datetime import datetime, timedelta
import investpy
import pandas as pd


def main():
    # Hoje
    today = datetime.utcnow().strftime("%d/%m/%Y")
    
    # Amanhã (para que o intervalo seja válido para API)
    tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%d/%m/%Y")

    # Busca a agenda do Investing com intervalo HOJE → AMANHÃ
    data = investpy.news.economic_calendar(
        from_date=today,
        to_date=tomorrow,
        importances=['high', 'medium'],
        countries=None,
    )

    df = pd.DataFrame(data)

    eventos = []

    for _, row in df.iterrows():
        # Converter data
        date = datetime.strptime(row['date'], "%d/%m/%Y").strftime("%Y-%m-%d")

        # Ignorar se não for hoje → mantém limpo
        if date != datetime.utcnow().strftime("%Y-%m-%d"):
            continue

        hora = row.get("time", "—")
        if "all" in hora.lower():
            hora = "00:00"

        eventos.append({
            "date": date,
            "time": hora,
            "country": row.get("currency", ""),
            "impact": row.get("importance", "").lower(),
            "title": row.get("event", "Sem título"),
            "previous": row.get("previous", "N/D"),
            "forecast": row.get("forecast", "N/D"),
            "actual": row.get("actual", "N/D")
        })

    # Salvar no formato do bot
    with open("today.json", "w", encoding="utf-8") as f:
        json.dump(eventos, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

