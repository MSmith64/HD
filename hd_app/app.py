from __future__ import annotations

import html
from pathlib import Path
from datetime import date, time

import streamlit as st

from hd_engine import compute_chart
from bodygraph import render
from references import ReferenceManager, REFERENCE_URLS

st.set_page_config(page_title="Personal Human Design Report", page_icon="◈", layout="wide")

DISCLAIMER = """**Non-commercial, private-use software.** This program is provided solely for personal, educational, and research use. It is not a commercial service, and it does not provide medical, psychological, legal, financial, or other professional advice. Human Design is presented as a reflective/spiritual system, not as a scientifically validated diagnostic method. Use the output as personal-interest material only."""

st.markdown("""
<style>
:root { --ink:#22283d; --brass:#9c7b33; --paper:#fffdf8; --muted:#6e6a60; }
.block-container{max-width:1250px;padding-top:2rem;padding-bottom:3rem}
.hd-title{font-family:Georgia,serif;font-size:2.4rem;color:var(--ink);letter-spacing:.03em;margin-bottom:.2rem}
.hd-sub{color:var(--muted);margin-bottom:1.5rem}
.card{border:1px solid #ddd7c9;border-radius:14px;padding:1rem 1.2rem;background:#fffdf8;margin-bottom:1rem}
.smallcaps{font-size:.76rem;letter-spacing:.13em;text-transform:uppercase;color:#80785f}
.metric{font-family:Georgia,serif;font-size:1.45rem;color:var(--ink)}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hd-title">Personal Human Design Report</div>', unsafe_allow_html=True)
st.markdown('<div class="hd-sub">Birth-data → bodygraph → planetary activations → reference excerpts</div>', unsafe_allow_html=True)
st.warning(DISCLAIMER)

with st.sidebar:
    st.header("Birth data")
    person_name=st.text_input("Name", value="Private chart")
    d=st.date_input("Date of birth", value=date(1990,1,1), min_value=date(1900,1,1), max_value=date(2100,12,31))
    t=st.time_input("Local time of birth", value=time(12,0))
    place=st.text_input("Place of birth", value="London, UK", help="City, region, country works best. The app geocodes the place to determine the historical time zone.")
    tz_override=st.text_input("Optional IANA time zone override", value="", placeholder="e.g. Europe/London")
    load_refs=st.checkbox("Load supplied reference PDFs", value=True)
    generate=st.button("Generate chart", type="primary", use_container_width=True)
    st.caption("References are fetched on demand and cached locally; the PDFs are not bundled into this repository.")

@st.cache_resource(show_spinner=False)
def refs_manager():
    return ReferenceManager(Path('.cache')/'references')

@st.cache_data(show_spinner=False)
def geocode_place(place: str):
    from geopy.geocoders import Nominatim
    from timezonefinder import TimezoneFinder
    geolocator=Nominatim(user_agent='hd-personal-chart/1.0', timeout=15)
    loc=geolocator.geocode(place)
    if not loc: raise ValueError(f"Could not geocode '{place}'. Try a more specific city/region/country.")
    tz=TimezoneFinder().timezone_at(lat=loc.latitude,lng=loc.longitude)
    if not tz: raise ValueError("Could not determine the IANA time zone for that place.")
    return {"display":loc.address,"lat":loc.latitude,"lon":loc.longitude,"timezone":tz}

if generate:
    with st.spinner("Resolving birthplace and calculating chart…"):
        try:
            geo=geocode_place(place) if not tz_override else {"display":place,"timezone":tz_override}
            chart=compute_chart(name=person_name, year=d.year, month=d.month, day=d.day, hour=t.hour, minute=t.minute, tz_name=geo['timezone'], place_label=geo['display'])
            st.session_state['chart']=chart; st.session_state['geo']=geo
        except Exception as e:
            st.error(str(e))

chart=st.session_state.get('chart')
if not chart:
    st.info("Enter the birth data and select **Generate chart**.")
    st.stop()

geo=st.session_state.get('geo',{})
if load_refs:
    rm=refs_manager()
    with st.spinner("Loading reference material…"):
        statuses=rm.load_all()
    bad=[(k,v) for k,v in statuses.items() if v.startswith('loaded') is False]
    if bad: st.warning("Some reference PDFs could not be loaded right now. Calculations still work; source excerpts will be omitted until the references are available.")
else:
    rm=refs_manager()

st.success(f"Birthplace: {chart['place']} · Time zone: {geo.get('timezone',tz_override)}")

cols=st.columns(6)
for c,label,val in zip(cols,["Type","Aura","Profile","Authority","Definition","Signature"],[chart['type'],chart['aura_type'].split(':')[0],chart['profile'],chart['authority'],chart['definition'],chart['signature']]):
    with c:
        st.markdown(f'<div class="smallcaps">{html.escape(label)}</div><div class="metric">{html.escape(str(val))}</div>', unsafe_allow_html=True)

left,right=st.columns([0.9,1.1])
with left:
    st.subheader("Bodygraph")
    svg=render(chart)
    st.components.v1.html(svg, height=1020, scrolling=False)
with right:
    st.subheader("Core chart")
    st.markdown(f"**Strategy:** {chart['strategy']}  ")
    st.markdown(f"**Energetic signature:** {chart['signature']}  ")
    st.markdown(f"**Not-self theme:** {chart['not_self']}  ")
    cross_ref = rm.cross_name(chart['cross']['gates'][0], chart['cross']['angle']) if 'rave' in rm.docs else {'available':False}
    cross_name = cross_ref.get('name') if cross_ref.get('available') else 'Source name unavailable'
    st.markdown(f"**Incarnation cross:** {chart['cross']['angle']} · {cross_name} · gates {chart['cross']['gates']}")
    if cross_ref.get('available'): st.caption(f"Source page {cross_ref['page']} · {cross_ref['source_url']}")
    st.markdown("**Defined centers:** " + ", ".join(chart['defined_centers']))
    st.markdown("**Open centers:** " + ", ".join(chart['open_centers']))
    st.markdown("**Active gates:** " + ", ".join(map(str, chart['active_gates'])))

st.divider()
st.subheader("Planetary placements")
rows=[]
for side,label in [("personality","Personality / Conscious"),("design","Design / Unconscious")]:
    st.markdown(f"### {label}")
    for key,a in chart[side].items():
        ref=rm.gate_entry(a['gate'],a['line']) if 'rave' in rm.docs else {"available":False}
        c1,c2,c3,c4,c5,c6,c7=st.columns([1.2,1.1,.7,.7,.7,.7,2.8])
        with c1: st.markdown(f"**{a['glyph']} {a['label']}**")
        with c2: st.write(f"Gate {a['gate']} · line {a['line']}")
        with c3: st.write(f"C{a['color']}")
        with c4: st.write(f"T{a['tone']}")
        with c5: st.write(f"B{a['base']}")
        with c6: st.write(a['sign'])
        with c7:
            if ref.get('available'):
                st.write(f"Gate excerpt (p. {ref['page']}): {ref['gate_excerpt']}")
                st.caption(f"Line {a['line']} excerpt: {ref['line_excerpt']}")
                pol=[]
                if ref.get('exaltation'): pol.append('Exalted: '+', '.join(ref['exaltation']))
                if ref.get('detriment'): pol.append('Detriment: '+', '.join(ref['detriment']))
                if pol: st.caption(' · '.join(pol))
            else:
                st.caption("Rave I’Ching reference not available in this session.")
    st.write("")

st.divider()
st.subheader("Active channels")
if not chart['channels']:
    st.info("No full channels are defined in this chart.")
else:
    for ch in chart['channels']:
        info=rm.channel_excerpt(*ch['gates']) if any(k.startswith('channels_') for k in rm.docs) else {"available":False}
        with st.expander(f"{ch['gates'][0]}–{ch['gates'][1]} · {ch['name']}"):
            st.write(f"Centers: {ch['centers'][0]} ↔ {ch['centers'][1]}")
            if info.get('available'):
                st.markdown(f"> {info['excerpt']}")
                st.caption(f"Source page {info['page']} · {info['source_url']}")
            else:
                st.caption("Channel reference excerpt unavailable in this session.")

st.divider()
st.subheader("Reference status")
for key,url in REFERENCE_URLS.items():
    ok=key in rm.docs
    st.write(("✅" if ok else "⚠️")+f" {key}: {url}")

st.caption("Private-use software. No account, analytics, advertising, or payments are implemented by this app.")
