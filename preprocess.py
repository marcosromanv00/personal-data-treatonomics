import csv
import json
from collections import Counter
import re

csv_path = 'ENCUESTA – TREATONOMICS  (Respuestas) - Respuestas de formulario 1.csv'

def clean_label(label):
    return re.sub(r'\s+', ' ', label).strip()

def get_counts_multi(data_list):
    counts = Counter()
    for item in data_list:
        if item:
            parts = [p.strip() for p in item.split(',')]
            counts.update(parts)
    return dict(counts)

try:
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    headers = reader.fieldnames
    
    mapping = {}
    for h in headers:
        if "1.Edad" in h: mapping['edad'] = h
        if "2.Situación actual" in h: mapping['situacion'] = h
        if "3.¿Qué tan importante" in h: mapping['ahorro'] = h
        if "4.¿Con qué frecuencia" in h: mapping['compra_freq'] = h
        if "5.¿Se ha dado" in h: mapping['gustos'] = h
        if "6.Cuando realiza" in h: mapping['justifica'] = h
        if "Si respondió \"\"Sí\"\"" in h or "Si respondió \"Sí\"" in h: mapping['frase'] = h
        if "7.Antes de realizar" in h: mapping['pre'] = h
        if "8.Después de realizarla" in h: mapping['post'] = h
        if "9.¿Qué tan frecuentemente" in h: mapping['redes_freq'] = h
        if "10.¿Alguna vez" in h: mapping['influ_real'] = h
        if "11.¿Qué tipo de contenido" in h: mapping['contenido'] = h
        if "12.¿Considera que" in h: mapping['influ_perc'] = h
        if "13.¿Cree que su comportamiento" in h: mapping['coherencia'] = h

    res = {
        'total': len(rows),
        'edad': Counter(row[mapping['edad']] for row in rows),
        'situacion': Counter(row[mapping['situacion']] for row in rows),
        'ahorro': Counter(row[mapping['ahorro']] for row in rows),
        'compra_freq': Counter(row[mapping['compra_freq']] for row in rows),
        'justificaciones': Counter(row[mapping['frase']] for row in rows if row[mapping['frase']]),
        'pre': get_counts_multi(row[mapping['pre']] for row in rows),
        'post': get_counts_multi(row[mapping['post']] for row in rows),
        'redes_freq': Counter(row[mapping['redes_freq']] for row in rows),
        'influ_real': Counter(row[mapping['influ_real']] for row in rows),
        'contenido': get_counts_multi(row[mapping['contenido']] for row in rows),
        'influ_perc': Counter(row[mapping['influ_perc']] for row in rows),
        'coherencia': Counter(row[mapping['coherencia']] for row in rows),
        'gustos': Counter(row[mapping['gustos']] for row in rows),
        'justifica_bin': Counter(row[mapping['justifica']] for row in rows),
        'questions': {k: v for k, v in mapping.items()}
    }

    reward_count = sum(1 for row in rows if any(x in (row[mapping['frase']] or "") for x in ["Me lo merezco", "Para eso trabajo"]))
    res['kpi_reward'] = round((reward_count / len(rows)) * 100, 2)

    dissonance_count = sum(1 for row in rows if (row[mapping['ahorro']] in ['4', '5']) and (row[mapping['coherencia']] in ['No', 'Parcialmente']))
    res['kpi_dissonance'] = round((dissonance_count / len(rows)) * 100, 2)

    digital_count = sum(1 for row in rows if row[mapping['influ_real']] == 'Sí' or row[mapping['influ_perc']] == 'Sí')
    res['kpi_digital'] = round((digital_count / len(rows)) * 100, 2)

    with open('data.json', 'w', encoding='utf-8') as out:
        json.dump(res, out, indent=4, ensure_ascii=False)
    
    print("Pre-processing complete. data.json created.")

except Exception as e:
    print(f"Error: {e}")
