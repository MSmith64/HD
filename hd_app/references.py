from __future__ import annotations

import io, os, re, hashlib, textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
import requests

REFERENCE_URLS = {
    "rave": "https://files.catbox.moe/v37woo.pdf",
    "channels_1": "https://files.catbox.moe/in3ce6.pdf",
    "channels_2": "https://files.catbox.moe/j3lkk5.pdf",
    "channels_3": "https://files.catbox.moe/eckryp.pdf",
    "channels_4": "https://files.catbox.moe/jwqf3f.pdf",
}

@dataclass
class DocIndex:
    name: str
    url: str
    path: Path
    pages: list[str]

class ReferenceManager:
    def __init__(self, cache_dir: str | Path):
        self.cache = Path(cache_dir); self.cache.mkdir(parents=True, exist_ok=True)
        self.docs: dict[str, DocIndex] = {}

    def _cached_path(self, key: str, url: str) -> Path:
        h=hashlib.sha256(url.encode()).hexdigest()[:12]
        return self.cache / f"{key}-{h}.pdf"

    def fetch_and_index(self, key: str) -> tuple[bool,str]:
        url=REFERENCE_URLS[key]; path=self._cached_path(key,url)
        try:
            if not path.exists() or path.stat().st_size < 5000:
                r=requests.get(url, timeout=30, headers={'User-Agent':'HD-Personal-Chart/1.0'})
                r.raise_for_status(); path.write_bytes(r.content)
            pdf=fitz.open(path); pages=[p.get_text('text') for p in pdf]
            self.docs[key]=DocIndex(key,url,path,pages)
            return True, f"loaded {len(pages)} pages"
        except Exception as e:
            self.docs.pop(key,None)
            return False, str(e)

    def load_all(self) -> dict[str,str]:
        return {k:self.fetch_and_index(k)[1] for k in REFERENCE_URLS}

    def _rave_page_for_gate(self, gate: int) -> Optional[int]:
        doc=self.docs.get('rave');
        if not doc: return None
        pat=re.compile(rf"(?m)^\s*{gate}\s*$")
        for i,text in enumerate(doc.pages):
            if pat.search(text) and 'THE GATE OF' in text.upper(): return i
        # fallback: search gate-of line
        for i,text in enumerate(doc.pages):
            if f"THE GATE OF" in text.upper() and re.search(rf"\b{gate}\b", text): return i
        return None

    def gate_entry(self, gate:int, line:int, max_words:int=25) -> dict:
        doc=self.docs.get('rave');
        if not doc: return {"available":False,"message":"Rave I’Ching reference is not loaded."}
        p=self._rave_page_for_gate(gate)
        if p is None: return {"available":False,"message":f"Gate {gate} was not located in the reference."}
        # The gate overview is generally on p and the six line descriptions on p+1.
        gate_text=' '.join(doc.pages[p].split())
        line_text=' '.join(doc.pages[p+1].split()) if p+1<len(doc.pages) else ''
        gate_excerpt=self._quote_words(gate_text, max_words, skip_prefix=max(0, gate_text.upper().find('THE GATE OF')))
        block=self._line_block(line_text, line)
        line_excerpt=self._quote_words(block, max_words)
        ex, det=self._planet_polarities(block)
        return {"available":True,"page":p+1,"gate_excerpt":gate_excerpt,"line_excerpt":line_excerpt,"exaltation":ex,"detriment":det,"source_url":doc.url}

    def _quote_words(self,text:str,max_words:int,start:int=0)->str:
        s=text[start:]
        # Prefer prose after heading/name rather than index boilerplate.
        s=re.sub(r"^\s*\d+\s+THE GATE OF[^.]*\.\s*",'',s,flags=re.I)
        words=s.split(); return ' '.join(words[:max_words]) + ('…' if len(words)>max_words else '')


    def _line_block(self, text:str, line:int)->str:
        # PyMuPDF usually keeps each numbered line heading at the start of a line.
        # Find the requested heading, then stop at the next numbered heading.
        starts=list(re.finditer(r"(?m)^\s*([1-6])\s+[^\n]{2,100}", text))
        for i,m in enumerate(starts):
            if int(m.group(1))==line:
                end=starts[i+1].start() if i+1<len(starts) else len(text)
                return text[m.start():end].strip()
        # Compact extraction fallback.
        m=re.search(rf"(?<!\d){line}\s+[A-Z][A-Za-z'’\- ]{{2,90}}", text)
        if m:
            end=re.search(r"\s+[1-6]\s+[A-Z]", text[m.end():])
            return text[m.start():m.end()+end.start() if end else len(text)].strip()
        return text

    def _planet_polarities(self, text:str):
        planets=["Sun","Earth","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]
        ex=[]; det=[]
        clean=' '.join(text.split())
        for planet in planets:
            if re.search(rf"\b{re.escape(planet)}\b[^.{{}}]{{0,180}}\bexalted\b", clean, re.I): ex.append(planet)
            if re.search(rf"\b{re.escape(planet)}\b[^.{{}}]{{0,180}}\bdetriment\b", clean, re.I): det.append(planet)
        return sorted(set(ex)), sorted(set(det))

    def cross_name(self, gate:int, angle:str)->dict:
        doc=self.docs.get('rave')
        if not doc: return {"available":False}
        p=self._rave_page_for_gate(gate)
        if p is None: return {"available":False}
        text=' '.join(doc.pages[p].split())
        labels={"Right Angle":r"THE RIGHT ANGLE CROSS OF (.+?)(?=THE JUXTAPOSITION CROSS OF)",
                "Juxtaposition":r"THE JUXTAPOSITION CROSS OF (.+?)(?=THE LEFT ANGLE CROSS OF)",
                "Left Angle":r"THE LEFT ANGLE CROSS OF (.+?)$"}
        m=re.search(labels.get(angle,''), text, re.I)
        if not m: return {"available":False}
        value=re.sub(r"\s+"," ",m.group(1)).strip()
        value=re.sub(r"\s+\(\d+\)$","",value).strip()
        return {"available":True,"name":value,"page":p+1,"source_url":doc.url}

    def _line_excerpt(self,text:str,line:int,max_words:int)->str:
        # Find the line heading, then capture until the next line heading. PDF text ordering varies, so fall back to whole page.
        m=re.search(rf"(?m)(?:^|\s){line}\s+[A-Z][A-Za-z'\-/& ]{{2,80}}(?=\s+\d\s+[A-Z]|$)",text)
        if m:
            s=text[m.start():m.end()]
        else:
            s=text
        words=s.split(); return ' '.join(words[:max_words]) + ('…' if len(words)>max_words else '')

    def channel_excerpt(self, a:int,b:int,max_words:int=25)->dict:
        needles=[f"{a}-{b}",f"{b}-{a}",f"{a} / {b}",f"{b} / {a}"]
        for key,doc in self.docs.items():
            if not key.startswith('channels_'): continue
            for idx,text in enumerate(doc.pages):
                loc=min([text.find(n) for n in needles if text.find(n)>=0], default=-1)
                if loc>=0:
                    snippet=' '.join(text[loc:loc+1200].split())
                    return {"available":True,"page":idx+1,"excerpt":" ".join(snippet.split()[:max_words])+('…' if len(snippet.split())>max_words else ''),"source_url":doc.url}
        return {"available":False,"message":f"No channel text found for {a}-{b}."}
