import json
from datetime import datetime
import investpy
import pandas as pd


def main():
    # Data de hoje no padrão dd/mm/yyyy
    today = datetime.utcnow().strftime("%d/%m/%Y")

    # Busca do dia atual com intervalo válido (Investing exige range)
    data = investpy.news.economic_calendar(
        from_date=today,
        to_date=today,
        countries=None,
        importances=['high', 'medium']
    )

    df = pd.DataFrame(data)

    eventos = []

    for _, row in df.iterrows():
        # Converte formato para yyyy-mm-dd
        date = datetime.strptime(row['date'], "%d/%m/%Y").strftime("%Y-%m-%d")

        hora = row.get("time", "—")
        if str(hora).lower() == "all day":
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

    with open("today.json", "w", encoding="utf-8") as f:
        json.dump(eventos, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
