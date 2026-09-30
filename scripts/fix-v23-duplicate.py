from pathlib import Path
p=Path("index.html")
s=p.read_text(encoding="utf-8")
needle="    function generateRhythm(opts) {"
first=s.find(needle)
second=s.find(needle, first+len(needle)) if first>=0 else -1
if second>=0 and "function generateRhythmLegacy(opts)" not in s:
    s=s[:second]+s[second:].replace(needle,"    function generateRhythmLegacy(opts) {",1)
    p.write_text(s,encoding="utf-8")
