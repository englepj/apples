# Apple Pit Market

A projector-run double-auction game for Principles of Microeconomics. Students get a
private buyer card (a value) or seller card (a cost), trade crates of apples in an open
outcry pit, and the instructor records each trade. The trade tape updates live, and the
debrief tab builds the step supply and demand curves from the cards.

This repo wraps the game (`apple_pit_market.html`) in a small Streamlit app that adds:

- **An instructor passcode.** Until you unlock it from the sidebar, the *Setup & cards*
  tab, which lists every card's value and cost, is hidden.
- **Working downloads** for the printable cards and the results CSV.

## Run it locally

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then edit the passcode
streamlit run streamlit_app.py
```

## Deploy on Streamlit Community Cloud

1. New app → pick this repo, branch `main`, main file `streamlit_app.py`.
2. In the app's **Settings → Secrets**, add:
   ```toml
   apple_pit_passcode = "your-passcode"
   ```

## Running a class

1. Before class, open the sidebar, unlock with the passcode, set the class size on
   *Setup & cards*, **deal a new deck**, and download the printable cards.
2. Lock the app again before you put it on the projector.
3. Record trades on the *Trading floor* tab; use *Next round…* for shocks, taxes and
   price controls; switch to *Debrief* at the end.

Trades are saved in the instructor's browser (local storage), so a refresh doesn't lose a
round. Each person who opens the app gets their own separate copy of the game, and
nothing about students is stored; cards are tracked by number.
