# Classroom Market Games

Projector-run economics games for Principles of Microeconomics, in one Streamlit app.
Pick a game from the sidebar:

- **🍎 Apple Pit Market**: supply and demand. Students get a private buyer card (a value)
  or seller card (a cost), trade crates of apples in an open-outcry pit, and the instructor
  records each trade. The trade tape updates live, and the debrief builds the step supply
  and demand curves from the cards.
- **🌮 Food Truck Friday**: consumer choice. Students spend a budget on tacos and
  smoothies using a points sheet for their eater type; the instructor tallies by show of
  hands. The debrief shows the budget line, the class demand curve for tacos, and the
  substitution and income effects.
- **✈️ Paper Airplane Factory**: production and cost. Each group runs a factory with one
  desk and one pen and adds a worker every round; inspectors count the planes that pass.
  The debrief turns the class's output into MP, AP, MC, AVC, and ATC, and an optional
  second run with more capital compares short-run cost curves.

Each game is a self-contained HTML file. `streamlit_app.py` wraps them and adds:

- **One instructor passcode** (`applesgame`) for every game. Until you unlock it from the
  sidebar, each game's Setup tab (Apple Pit's card values, Food Truck Friday's points
  tables) is hidden. It's a light lock to keep setup details off the projector, not real
  security.
- **Working downloads** for the printable cards/sheets and the results CSVs.
- **A link for each game**: add `?game=apples`, `?game=foodtruck`, or `?game=planes` to the app's address.

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

1. Before class, open the sidebar (» at the top left), pick the game, and unlock with
   `applesgame`. On the Setup tab, set the class size and download the printable cards
   (Apple Pit: **deal a new deck** first), sheets (Food Truck Friday), or the factory kit
   (Paper Airplane Factory).
2. Lock the app again before you put it on the projector.
3. Run the rounds on the first tab, use *Next round…* to change the rules or prices, and
   switch to *Debrief* at the end.

Each game saves its rounds in the instructor's browser (local storage), so a refresh or a
switch between games doesn't lose anything. Each person who opens the app gets their own
separate copy, and nothing about students is stored.

## Adding another game

Put the game's HTML file in this folder and add an entry to `GAMES` at the top of
`streamlit_app.py`. If the game has a Setup tab with the ids `tab-setup` and `view-setup`,
the passcode hides it automatically.
