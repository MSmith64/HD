# Personal Human Design Report

Non-commercial, private-use web application for generating a Human Design bodygraph and natal-style report from birth date, time, and place.

## What it does

- Calculates Personality and Design planetary activations using Swiss Ephemeris.
- Maps each placement to Gate / Line / Color / Tone / Base.
- Determines Type, aura type, Profile, Strategy, Authority, Definition, signature, not-self theme, defined/open centers, active gates, active channels, and the four-gate incarnation-cross signature.
- Renders an SVG bodygraph in the browser.
- Loads the supplied Rave I'Ching and channel-reference PDFs at runtime and displays short source-linked excerpts for the relevant gate/line/channel.
- Does not bundle the supplied copyrighted PDFs into the repository.
- Includes an explicit non-commercial/private-use disclaimer in the UI and documentation.

## Reference material

The app is configured with these supplied sources:

- Rave I'Ching: https://files.catbox.moe/v37woo.pdf
- Channels: https://files.catbox.moe/in3ce6.pdf
- Channels: https://files.catbox.moe/j3lkk5.pdf
- Channels: https://files.catbox.moe/eckryp.pdf
- Channels: https://files.catbox.moe/jwqf3f.pdf

The app fetches them on first use and caches them locally. If a host cannot reach the URLs, chart calculation still works and the reference-excerpt areas show as unavailable.

## Install / run locally

A normal Python environment can install the full dependency set automatically from `requirements.txt`:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Deploy from GitHub

Push this directory to a GitHub repository and deploy it with Streamlit Community Cloud using `app.py` as the entry point. Streamlit installs `requirements.txt` automatically during deployment.

## Dependency note

The app uses the Swiss Ephemeris Python bindings (`pyswisseph`) for planetary longitudes and `timezonefinder` + `geopy` to turn a birthplace string into an IANA time zone. An optional time-zone override is available for locations where automated geocoding is ambiguous.

## License / private-use notice

The application source is provided for personal, educational, and research use only. It is not a commercial Human Design service. The supplied Rave I'Ching and channel PDFs remain external reference material and are not redistributed by this repository.

Human Design is presented as a reflective/spiritual framework, not as a scientifically validated diagnostic system.
