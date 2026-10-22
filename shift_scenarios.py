"""Scenario bank for Shift Happens.

Each scenario:
  id       short unique key
  kind     "curve" (which curve shifts?), "outcome" (what happens to P and Q?),
           "double" (two shifts at once), or "trap" (shift vs. movement along)
  market   the market being analyzed (shown in bold)
  text     the news event students read
  options  answer choices (2-5)
  answer   index of the correct option
  d, s     horizontal shift of demand / supply for the reveal graph
           (+ = right / increase, - = left / decrease, 0 = no shift)
  graph    optional "move" = draw a movement along demand instead of a shift
  why      one- or two-sentence explanation shown on reveal

Edit freely: add, remove, or reword. The app picks up whatever is in SCENARIOS.
"""

CURVE = [
    "Demand increases (shifts right)",
    "Demand decreases (shifts left)",
    "Supply increases (shifts right)",
    "Supply decreases (shifts left)",
]

OUTCOME = [
    "Price ↑, Quantity ↑",
    "Price ↑, Quantity ↓",
    "Price ↓, Quantity ↑",
    "Price ↓, Quantity ↓",
]

DOUBLE = [
    "Price ↑, Quantity ambiguous",
    "Price ↓, Quantity ambiguous",
    "Price ambiguous, Quantity ↑",
    "Price ambiguous, Quantity ↓",
]

TRAP = CURVE[:3] + ["No shift — a movement along the demand curve"]

KIND_LABELS = {
    "curve": "Which curve shifts?",
    "outcome": "Price & quantity",
    "double": "Double shift",
    "trap": "Shift or movement?",
}

SCENARIOS = [
    # ---------- Which curve shifts? ----------
    dict(id="iced_coffee", kind="curve", market="Iced coffee in the Tri-Cities",
         text="A week-long heat wave hits eastern Washington.",
         options=CURVE, answer=0, d=3, s=0,
         why="Weather changes buyers' tastes and preferences: more people want iced coffee at every price, so demand shifts right."),
    dict(id="apple_frost", kind="curve", market="Washington apples",
         text="A late spring frost kills a large share of the apple blossoms in the Yakima Valley.",
         options=CURVE, answer=3, d=0, s=-3,
         why="Fewer apples can be grown at any price: a natural event reduces the number of apples producers can bring to market, so supply shifts left."),
    dict(id="cherry_robot", kind="curve", market="Sweet cherries",
         text="A new robotic harvester cuts the labor cost of picking cherries by 30%.",
         options=CURVE, answer=2, d=0, s=3,
         why="Better technology lowers the cost of production, so growers are willing to sell more at every price: supply shifts right."),
    dict(id="energy_drink", kind="curve", market="Energy drinks",
         text="A widely reported study links daily energy-drink use to heart problems in young adults.",
         options=CURVE, answer=1, d=-3, s=0,
         why="Information that changes tastes and preferences lowers how much buyers want at every price: demand shifts left."),
    dict(id="buns", kind="curve", market="Hot dog buns",
         text="Grocery stores slash the price of hot dogs for the Fourth of July.",
         options=CURVE, answer=0, d=3, s=0,
         why="Hot dogs and buns are complements. Cheaper hot dogs mean more hot dogs bought, and more buns wanted at every bun price: demand for buns shifts right."),
    dict(id="coke", kind="curve", market="Coca-Cola",
         text="PepsiCo raises the price of Pepsi by 20%.",
         options=CURVE, answer=0, d=3, s=0,
         why="Pepsi and Coke are substitutes. When Pepsi gets pricier, some buyers switch to Coke: demand for Coke shifts right."),
    dict(id="used_cars", kind="curve", market="Used cars",
         text="A recession lowers household incomes across the region.",
         options=CURVE, answer=0, d=3, s=0,
         why="Used cars are typically an inferior good: when income falls, people trade down from new cars, so demand for used cars shifts right. (The trap is assuming every demand falls in a recession.)"),
    dict(id="vape_tax", kind="curve", market="Vape cartridges",
         text="The state adds a $1 excise tax on every vape cartridge, collected from sellers.",
         options=CURVE, answer=3, d=0, s=-3,
         why="A per-unit tax on sellers raises their cost of supplying each unit, so supply shifts left (up by the amount of the tax)."),
    dict(id="soybeans", kind="curve", market="Soybeans",
         text="The price of corn jumps after a surge in ethanol demand.",
         options=CURVE, answer=3, d=0, s=-3,
         why="Corn and soybeans compete for the same farmland (substitutes in production). Higher corn prices pull acres into corn, so soybean supply shifts left."),
    dict(id="gas_expect", kind="curve", market="Gasoline today",
         text="News reports say gas prices will jump sharply starting next week.",
         options=CURVE, answer=0, d=3, s=0,
         why="Buyers' expectations of a higher future price make them fill up now: today's demand shifts right."),

    # ---------- Shift or movement? ----------
    dict(id="concert", kind="trap", market="Concert tickets",
         text="The promoter raises ticket prices, and fewer fans buy tickets.",
         options=TRAP, answer=3, d=0, s=0, graph="move",
         why="A change in the good's own price never shifts its demand curve. Fans move up along the existing demand curve to a smaller quantity demanded."),
    dict(id="coffee_price", kind="trap", market="Starbucks lattes",
         text="Starbucks puts lattes on sale for half price, and lines get longer.",
         options=TRAP, answer=3, d=0, s=0, graph="move_down",
         why="Again the good's own price changed: that's a movement down along the demand curve to a larger quantity demanded, not a shift."),

    # ---------- Price & quantity ----------
    dict(id="wineries", kind="outcome", market="Local wine",
         text="Twenty new wineries open in Benton County over two years.",
         options=OUTCOME, answer=2, d=0, s=3,
         why="More sellers shifts supply right. Moving down along demand, price falls and quantity rises."),
    dict(id="boots", kind="outcome", market="Brand X boots",
         text="A pop star wears Brand X boots on a world tour, and the photos go viral.",
         options=OUTCOME, answer=0, d=3, s=0,
         why="Tastes shift demand right. Moving up along supply, both equilibrium price and quantity rise."),
    dict(id="burgers", kind="outcome", market="Fast-food burgers",
         text="A higher minimum wage raises labor costs at fast-food restaurants.",
         options=OUTCOME, answer=1, d=0, s=-3,
         why="Higher input costs shift supply left. Moving up along demand, price rises and quantity falls."),
    dict(id="parking", kind="outcome", market="Downtown parking",
         text="Many employers switch to permanent remote work, and commuting drops.",
         options=OUTCOME, answer=3, d=-3, s=0,
         why="Fewer commuters shifts demand left. Moving down along supply, both price and quantity fall."),

    # ---------- Double shifts ----------
    dict(id="pizza", kind="double", market="Pizza",
         text="Football season starts (more pizza parties) at the same time cheese prices spike.",
         options=DOUBLE, answer=0, d=3, s=-2,
         why="Demand right pushes P and Q up; supply left pushes P up and Q down. Price rises for sure; the change in quantity depends on which shift is bigger."),
    dict(id="solar", kind="double", market="Rooftop solar panels",
         text="Panel manufacturing costs fall, and the state also launches a rebate for homeowners who install solar.",
         options=DOUBLE, answer=2, d=3, s=3,
         why="Both shifts push quantity up. Demand right raises price, supply right lowers it, so the price change is ambiguous."),
    dict(id="hay", kind="double", market="Hay",
         text="A drought cuts the hay harvest, and fewer families are keeping horses.",
         options=DOUBLE, answer=3, d=-2, s=-3,
         why="Both shifts push quantity down. Supply left raises price, demand left lowers it, so the price change is ambiguous."),
    dict(id="evs", kind="double", market="Electric vehicles",
         text="Battery costs fall sharply while gasoline gets much cheaper.",
         options=DOUBLE, answer=1, d=-2, s=3,
         why="Supply right lowers P and raises Q; cheaper gas (a substitute's operating cost) shifts EV demand left, lowering P and Q. Price falls for sure; quantity is ambiguous."),
]

SCENARIO_BY_ID = {s["id"]: s for s in SCENARIOS}

# Light sanity check so a typo in an edit fails loudly at import time.
for _s in SCENARIOS:
    assert 0 <= _s["answer"] < len(_s["options"]), _s["id"]
    assert _s["kind"] in KIND_LABELS, _s["id"]
assert len(SCENARIO_BY_ID) == len(SCENARIOS), "duplicate scenario id"
