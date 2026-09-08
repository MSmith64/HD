from __future__ import annotations
from html import escape
from hd_engine import CHANNELS

VIEW_W, VIEW_H = 851.41, 1309.4
VB_Y0 = -104
INK = "#22283d"; BRASS = "#9c7b33"; RED = "#9a4a3c"; HAIRLINE = "#cbc5b6"; PAPER = "#fffdf8"; OPEN_STROKE = "#8c8574"; FAINT = "#b3ab97"; INACTIVE_RING = "#9a9280"; INACTIVE_TXT = "#7c745f"
CENTER_POLY = {
    "Head": [(420,13),(334,158),(507,158)], "Ajna": [(334,209),(507,209),(420,360)], "Throat": [(343,399),(497,399),(497,559),(343,559)],
    "G": [(420,592),(521,694),(420,796),(320,694)], "Ego": [(606,744),(521,842),(670,842)], "Sacral": [(343,925),(497,925),(497,1079),(343,1079)],
    "SolarPlexus": [(680,975),(841,884),(841,1066)], "Spleen": [(167,975),(6,884),(6,1066)], "Root": [(343,1149),(497,1149),(497,1296),(343,1296)],
}
GATE_XY = {1:(420.8,616.0),2:(420.7,766.3),3:(420.7,1060.1),4:(458.2,228.6),5:(383.2,942.7),6:(712.6,976.7),7:(383.2,650.9),8:(425.2,540.0),9:(458.2,1060.1),10:(345.5,690.9),11:(458.2,263.4),12:(479.1,476.2),13:(458.2,650.9),14:(420.7,942.7),15:(383.2,734.7),16:(362.4,446.9),17:(383.2,262.0),18:(30.4,1031.5),19:(478.1,1202.3),20:(362.4,494.6),21:(604.1,770.2),22:(781.4,939.0),23:(420.7,416.3),24:(420.7,228.6),25:(492.6,699.5),26:(554.1,820.2),27:(363.5,1024.8),28:(62.6,1012.6),29:(458.2,942.7),30:(813.6,1031.5),31:(383.2,540.2),32:(95.7,993.8),33:(458.2,540.2),34:(363.5,978.7),35:(479.1,442.2),36:(813.6,918.3),37:(748.2,957.3),38:(363.4,1238.4),39:(478.1,1238.4),40:(638.0,820.2),41:(478.1,1274.6),42:(383.2,1060.1),43:(420.7,324.7),44:(95.7,957.2),45:(479.1,509.8),46:(458.2,734.7),47:(383.2,228.5),48:(30.4,918.4),49:(748.2,993.8),50:(131.4,976.7),51:(580.1,794.1),52:(458.2,1171.2),53:(383.2,1171.2),54:(363.4,1202.3),55:(780.8,1013.1),56:(458.2,416.3),57:(62.6,939.0),58:(363.4,1274.6),59:(476.4,1024.8),60:(420.7,1171.2),61:(420.8,140.0),62:(383.2,416.3),63:(457.4,140.0),64:(383.2,140.3)}
GATE_R=11.5

def _poly(pts, fill, stroke, sw):
    return f"<polygon points='{ ' '.join(f'{x},{y}' for x,y in pts)}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}'/>"

def _arrow(x,y,direction,color,s=11):
    pts=[(x+s,y-s),(x+s,y+s),(x-s,y)] if direction=='left' else [(x-s,y-s),(x-s,y+s),(x+s,y)]
    return f"<polygon points='{ ' '.join(f'{px:.0f},{py:.0f}' for px,py in pts)}' fill='{color}'/>"

def render(subj):
    defined=set(subj['defined_centers']); pers={p['gate'] for p in subj['personality'].values()}; des={p['gate'] for p in subj['design'].values()}; active=pers|des
    defined_pairs={frozenset(ch['gates']) for ch in subj['channels']}
    parts=[f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 {VB_Y0} {VIEW_W} {VIEW_H-VB_Y0}' font-family='Georgia, serif'>", f"<rect x='0' y='{VB_Y0}' width='{VIEW_W}' height='{VIEW_H-VB_Y0}' fill='{PAPER}'/>"]
    for name,pts in CENTER_POLY.items(): parts.append(_poly(pts, INK if name in defined else '#fff', INK if name in defined else OPEN_STROKE, 1.5 if name in defined else 2.2))
    def seg(x1,y1,x2,y2,color,w): return f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{color}' stroke-width='{w}' stroke-linecap='round'/>"
    for a,b,*_ in CHANNELS:
        if frozenset((a,b)) not in defined_pairs:
            parts.append(seg(*GATE_XY[a],*GATE_XY[b],FAINT,2))
    for a,b,*_ in CHANNELS:
        if frozenset((a,b)) in defined_pairs: continue
        x1,y1=GATE_XY[a]; x2,y2=GATE_XY[b]; mx,my=(x1+x2)/2,(y1+y2)/2
        for (gx,gy),g in [((x1,y1),a),((x2,y2),b)]:
            if g in active: parts.append(seg(gx,gy,mx,my, RED if g in des and g not in pers else INK, 4))
    for a,b,*_ in CHANNELS:
        if frozenset((a,b)) in defined_pairs: parts.append(seg(*GATE_XY[a],*GATE_XY[b],BRASS,6))
    for g in range(1,65):
        x,y=GATE_XY[g]; ip,idd=g in pers,g in des
        fill,txt,ring=(INK,'#fff',RED) if ip and idd else ((INK,'#fff',INK) if ip else ((RED,'#fff',RED) if idd else ('#fff',INACTIVE_TXT,INACTIVE_RING)))
        sw=3 if ip and idd else 1.4
        parts.append(f"<circle cx='{x}' cy='{y}' r='{GATE_R}' fill='{fill}' stroke='{ring}' stroke-width='{sw}'/><text x='{x}' y='{y+4.2}' text-anchor='middle' font-size='13' fill='{txt}'>{g}</text>")
    parts.append('</svg>'); return ''.join(parts)
