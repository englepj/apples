# Apple Pit Market

A projector-run double-auction game for Principles of Microeconomics. Students get a
private buyer card (a value) or seller card (a cost), trade crates of apples in an open
outcry pit, and the instructor records each trade. The trade tape updates live, and the
debrief tab builds the step supply and demand curves from the cards.

This repo wraps the game (`apple_pit_market.html`) in a small Streamlit app that adds:

- **An instructor passcode** (`applesgame`). Until you unlock it from the sidebar, the
  *Setup & cards* tab, which lists every card's value and cost, is hidden. It's a light
  lock to keep the cards off the projector, not real security.
- **Working downloads** for the printable cards and the results CSV.

## Run it locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy on Streamlit Community Cloud

New app → pick this repo, branch `main`, main file `streamlit_app.py`. No secrets are
needed. To change the passcode later, add `apple_pit_passcode = "something-else"` in the
app's **Settings → Secrets**; it overrides the default.

## Running a class

1. Before class, open the sidebar, unlock with `applesgame`, set the class size on
   *Setup & cards*, **deal a new deck**, and download the printable cards.
2. Lock the app again before you put it on the projector.
3. Record trades on the *Trading floor* tab; use *Next round…* for shocks, taxes and
   price controls; switch to *Debrief* at the end.

Trades are saved in the instructor's browser (local storage), so a refresh doesn't lose a
round. Each person who opens the app gets their own separate copy of the game, and
nothing about students is stored; cards are tracked by number.
