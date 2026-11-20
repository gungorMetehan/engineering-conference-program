#!/usr/bin/env python3
"""Validate editable program data and refresh pre-rendered HTML tables.

Run from any directory: python tools/sync_program.py [--check]
No third-party packages are required.
"""
import argparse
import datetime
import html
import json
from pathlib import Path
import re
import sys

months = {
    'tr': ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'],
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
}
weekdays = {
    'tr': ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'],
    'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
}
esc = lambda value: html.escape(str(value), quote=True)
coffee = '<svg width="27" height="27" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M4 8h12v8a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4V8ZM16 9h2a3 3 0 0 1 0 6h-2M7 2v3M12 2v3M2 22h17"/></svg>'

def date_text(d, l):
    date = datetime.date.fromisoformat(d)
    text = f'{date.day} {months[l][date.month - 1]} {date.year}'
    return text + ' ' + weekdays[l][date.weekday()] if l == 'tr' else weekdays[l][date.weekday()] + ', ' + text

def table(d, l):
    t = i18n[l]
    prefix = f"p-{l}-{d['day']}"
    out = '<caption class="sr-only">' + esc(date_text(d['date'], l)) + '</caption><thead><tr><th scope="col" class="timehead">' + t['time'] + '</th>'
    for i, r in enumerate(data['rooms']):
        out += f'''<th scope="col" id="{prefix}-h{i}"><span class="room-no"><i class="l{i}"></i>{t['room']} {i + 1:02}</span>{esc(r[l])}</th>'''
    out += '</tr></thead><tbody>'
    for e in d['events']:
        common = e['cells'][0]['type'] in ['break', 'lunch'] and all((c['type'] == e['cells'][0]['type'] for c in e['cells']))
        out += '<tr' + (' class="breakrow"' if common else '') + '><th scope="row"><time>' + esc(e['start']) + '</time><span>– ' + esc(e['end']) + '</span></th>'
        if common:
            out += '<td colspan="4"><div class="break-label">' + coffee + esc(t[e['cells'][0]['type']]) + '</div></td>'
        else:
            for i, c in enumerate(e['cells']):
                out += f'<td headers="{prefix}-h{i}">'
                if c['type'] == 'paper':
                    out += f'''<details class="paper track-{i}" data-id="{c['id']}"><summary><span class="paper-copy"><span class="title">{esc(c[l])}</span><span class="authors">''' + esc(' · '.join(c.get('authors', []))) + '</span></span><span class="plus" aria-hidden="true">+</span></summary><div class="abstract"><div class="label">' + t['abstract'] + '</div><p>' + esc(c['abstract'].get(l) or t['pending']) + '</p>'
                    if l == 'en':
                        out += '<p class="original">' + t['original'] + '<span lang="tr">' + esc(c['tr']) + '</span></p>'
                    out += '</div></details>'
                elif c['type'] != 'empty':
                    out += '<div class="event"><b>' + t['event'] + '</b>' + esc(c[l]) + '</div>'
                out += '</td>'
        out += '</tr>'
    return out + '</tbody>'


def minutes(value):
    hour, minute = map(int, value.split(':'))
    if not 0 <= hour < 24 or not 0 <= minute < 60:
        raise ValueError('Geçersiz saat: ' + value)
    return hour * 60 + minute


def validate(program):
    identifiers = set()
    total = 0
    errors = []
    for day in program['days']:
        datetime.date.fromisoformat(day['date'])
        records = []
        for event in day['events']:
            start, end = minutes(event['start']), minutes(event['end'])
            if start >= end:
                errors.append(f"Gün {day['day']}: başlangıç/bitiş saati hatalı.")
            if len(event['cells']) != len(program['rooms']):
                errors.append(f"Gün {day['day']}: salon sayısı ile hücre sayısı farklı.")
            for room, paper in enumerate(event['cells']):
                if paper['type'] != 'paper':
                    continue
                total += 1
                pid = paper['id']
                if pid in identifiers:
                    errors.append('Tekrarlanan bildiri kimliği: ' + pid)
                identifiers.add(pid)
                names = [' '.join(a.split()).casefold() for a in paper.get('authors', [])]
                if len(names) != len(set(names)):
                    errors.append(pid + ': aynı yazar iki kez yazılmış.')
                for language in ('tr', 'en'):
                    if not paper.get(language, '').strip():
                        errors.append(pid + ': bildiri başlığı boş (' + language + ').')
                    if len(paper.get('abstract', {}).get(language, '').split()) > 200:
                        errors.append(pid + ': özet 200 kelimeyi aşıyor (' + language + ').')
                for previous_start, previous_end, previous_room, previous_id, previous_names in records:
                    overlap = start < previous_end and previous_start < end
                    common = set(names).intersection(previous_names)
                    if room != previous_room and overlap and common:
                        errors.append(f"Gün {day['day']}, {event['start']}: {previous_id} / {pid} yazar çakışması: {', '.join(sorted(common))}")
                records.append((start, end, room, pid, names))
    if errors:
        raise ValueError('\n'.join(errors))
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Dosyayı değiştirmeden kontrol et.')
    options = parser.parse_args()
    target = Path(__file__).resolve().parent.parent / 'index.html'
    source = target.read_text(encoding='utf-8')
    match = re.search(r'<script[^>]*id="program-data"[^>]*>(.*?)</script>', source, re.S)
    if not match:
        raise ValueError('program-data bölümü bulunamadı.')
    global data, i18n
    data = json.loads(match.group(1))
    dictionary = re.search(r'var DATA, I18N = (.*?);\s*function byId', source, re.S)
    if not dictionary:
        raise ValueError('Çeviri sözlüğü bulunamadı.')
    i18n = json.loads(dictionary.group(1))
    total = validate(data)
    tables = []
    for day in data['days']:
        for language in ('tr', 'en'):
            markup = table(day, language)
            markup = re.sub(r'(<span class="room-no"><i class="l\d"></i>)(?:Salon|Hall) \d{2}(</span>)', r'\1\2', markup)
            tables.append('<table class="schedule">\n' + markup.replace('><', '>\n<') + '\n</table>')
    iterator = iter(tables)
    refreshed, count = re.subn(r'<table class="schedule">.*?</table>', lambda m: next(iterator), source, flags=re.S)
    if count != len(tables):
        raise ValueError('Hazır tablo sayısı beklenen sayı ile eşleşmiyor.')
    if options.check:
        if refreshed != source:
            raise ValueError('Hazır tablolar güncel değil. python tools/sync_program.py komutunu çalıştırın.')
        print(f'Kontrol başarılı: {total} bildiri; yazar çakışması yok; hazır tablolar güncel.')
    else:
        target.write_text(refreshed, encoding='utf-8')
        print(f'Güncellendi: {total} bildiri; {count} hazır tablo; yazar çakışması yok.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, StopIteration) as error:
        print('HATA: ' + str(error), file=sys.stderr)
        sys.exit(1)
