import json
from datetime import datetime
import investpy
import pandas as pd


def main():
    today_str = datetime.utcnow().strftime("%d/%m/%Y")

    data = investpy.news.economic_calendar(
        time_zone=None,
        time_filter='time_only',
        countries=None,
        importances=['high', 'medium'],
        from_date=today_str,
        to_date=today_str
    )

    df = pd.DataFrame(data)

    eventos = []

    for _, row in df.iterrows():
        try:
            data_formatada = datetime.strptime(row['date'], '%d/%m/%Y').strftime('%Y-%m-%d')
        except:
            continue

        hora = row.get('time', '—')
        if hora.lower() == 'all day':
            hora = '00:00'

        impacto = (row.get('importance') or "").lower()
        if impacto not in ('high', 'medium'):
            continue

        eventos.append({
            "date": data_formatada,
            "time": hora,
            "country": row.get("currency", ""),
            "impact": impacto,
            "title": row.get("event", "Sem título"),
            "previous": row.get("previous", "N/D"),
            "forecast": row.get("forecast", "N/D"),
            "actual": row.get("actual", "N/D")
        })

    with open("today.json", "w", encoding="utf-8") as arquivo:
        json.dump(eventos, arquivo, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
