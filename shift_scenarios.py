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

Numeric questions (kinds "surplus" and "control") use the MARKET below instead of
d/s and carry  num=dict(control=None | ("ceiling", price) | ("floor", price),
shade="eq" | "cs" | "ps" | "ts" | "all", labels="intercepts" | "points").
No equations are shown: the graph (with gridlines) appears with the question and
labels the intercepts, plus the corner points of the triangles when
labels="points", so students compute areas from those. The reveal shades CS, PS
and deadweight loss with dollar values worked out by the app.

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
    "surplus": "Surplus",
    "control": "Price controls",
}

# Groups for the deck picker on the presenter screen.
DECKS = {
    "Shifts": ["curve", "trap", "outcome", "double"],
    "Surplus & price controls": ["surplus", "control"],
}

# The numeric case (used to draw the graph; students never see the equations):
# linear demand P = a - b*Q and supply P = c + d*Q.
# Equilibrium: P = $8, Q = 12.  CS = $72, PS = $36, total = $108.
MARKET = dict(
    name="Peaches at the Pasco farmers' market",
    q_unit="crates per day",
    a=20, b=1,      # demand  P = 20 - Q
    c=2, d=0.5,     # supply  P = 2 + 0.5Q
)

CEILING_OUTCOME = [
    "Shortage of 6 crates",
    "Surplus of 6 crates",
    "Shortage of 4 crates",
    "No effect: the ceiling isn't binding",
]
FLOOR_OUTCOME = [
    "Surplus (excess supply) of 6 crates",
    "Shortage of 6 crates",
    "Surplus (excess supply) of 2 crates",
    "No effect: the floor isn't binding",
]

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


_M = MARKET["name"]

SCENARIOS += [
    # ---------- Surplus at equilibrium ----------
    dict(id="num_eq", kind="surplus", market=_M,
         text="Read the graph: what are the equilibrium price and quantity?",
         options=["P = $8, Q = 12", "P = $12, Q = 8", "P = $10, Q = 10", "P = $8, Q = 14"],
         answer=0, num=dict(control=None, shade="eq", labels="intercepts"),
         why="The curves cross at Q = 12 crates and P = $8. Every surplus triangle starts from this point."),
    dict(id="num_cs", kind="surplus", market=_M,
         text="How much consumer surplus is there at equilibrium?",
         options=["$72", "$144", "$36", "$96"],
         answer=0, num=dict(control=None, shade="cs", labels="points"),
         why="CS is the triangle under demand and above the price. Base: 12 crates. Height: from the $20 "
             "intercept down to $8, so $12. ½ × 12 × $12 = $72. ($144 forgets the ½.)"),
    dict(id="num_ps", kind="surplus", market=_M,
         text="How much producer surplus is there at equilibrium?",
         options=["$36", "$72", "$48", "$18"],
         answer=0, num=dict(control=None, shade="ps", labels="points"),
         why="PS is the triangle above supply and below the price. Base: 12 crates. Height: from $8 down to "
             "the $2 intercept, so $6. ½ × 12 × $6 = $36."),
    dict(id="num_ts", kind="surplus", market=_M,
         text="What is total surplus (CS + PS) at equilibrium, and is there any deadweight loss?",
         options=["$108, no deadweight loss", "$108, plus $12 deadweight loss",
                  "$72, no deadweight loss", "$144, no deadweight loss"],
         answer=0, num=dict(control=None, shade="ts", labels="points"),
         why="$72 + $36 = $108. The competitive equilibrium trades every crate worth more to a buyer than it "
             "costs a seller, so nothing is lost."),

    # ---------- Price ceiling ----------
    dict(id="ceil_effect", kind="control", market=_M,
         text="After a bad harvest, the city caps peach prices at $6 per crate. What happens?",
         options=CEILING_OUTCOME, answer=0, num=dict(control=("ceiling", 6), shade="all", labels="points"),
         why="Follow the $6 line: it meets supply at 8 crates and demand at 14. Buyers want 14 but sellers "
             "offer only 8. Shortage = 14 − 8 = 6, and only 8 crates actually trade."),
    dict(id="ceil_winlose", kind="control", market=_M,
         text="With the $6 price ceiling, who wins and who loses, and by how much? (Assume the 8 crates go "
              "to the buyers who value them most.)",
         options=["Consumers +$8, producers −$20", "Consumers +$20, producers −$20",
                  "Consumers −$8, producers +$20", "Consumers +$16, producers −$16"],
         answer=0, num=dict(control=("ceiling", 6), shade="all", labels="points"),
         why="Consumers gain $16 on the 8 crates they still buy ($2 off each) but lose the $8 triangle on the "
             "4 crates no longer sold: net +$8 (CS $72 → $80). Producers lose $20 (PS $36 → $16)."),
    dict(id="ceil_dwl", kind="control", market=_M,
         text="How big is the deadweight loss from the $6 price ceiling?",
         options=["$12", "$6", "$24", "$0, the shortage is just a transfer"],
         answer=0, num=dict(control=("ceiling", 6), shade="all", labels="points"),
         why="The 4 crates between Q = 8 and Q = 12 no longer trade. At Q = 8 buyers value a crate at $12 and it "
             "costs $6 to supply: ½ × 4 × ($12 − $6) = $12. Check: $108 − ($80 + $16) = $12."),
    dict(id="ceil_loose", kind="control", market=_M,
         text="Instead, suppose the city caps the price at $10 per crate. What happens?",
         options=["Nothing: price stays $8 and 12 crates trade", "Shortage of 6 crates",
                  "Surplus of 6 crates", "Price rises to the $10 cap"],
         answer=0, num=dict(control=("ceiling", 10), shade="all", labels="points"),
         why="A ceiling above the equilibrium price doesn't bind. The market still clears at $8, so CS, PS and "
             "total surplus are unchanged."),

    # ---------- Price floor ----------
    dict(id="floor_effect", kind="control", market=_M,
         text="To support growers, the state sets a minimum price of $10 per crate. What happens?",
         options=FLOOR_OUTCOME, answer=0, num=dict(control=("floor", 10), shade="all", labels="points"),
         why="Follow the $10 line: it meets demand at 10 crates and supply at 16. Sellers offer 16 but buyers "
             "want only 10. 6 crates go unsold, and only 10 trade."),
    dict(id="floor_winlose", kind="control", market=_M,
         text="With the $10 price floor, who wins and who loses, and by how much? (Assume the lowest-cost "
              "growers make the 10 sales and nobody buys the unsold crates.)",
         options=["Producers +$19, consumers −$22", "Producers +$22, consumers −$22",
                  "Producers +$20, consumers −$20", "Producers −$19, consumers +$22"],
         answer=0, num=dict(control=("floor", 10), shade="all", labels="points"),
         why="CS shrinks to the triangle above $10: ½ × 10 × ($20 − $10) = $50, down $22 from $72. "
             "PS rises from $36 to $55 (+$19): growers gain $20 on the 10 crates still sold ($2 more each) and "
             "lose $1 on the 2 crates no longer sold."),
    dict(id="floor_dwl", kind="control", market=_M,
         text="How big is the deadweight loss from the $10 price floor?",
         options=["$3", "$6", "$12", "$22"],
         answer=0, num=dict(control=("floor", 10), shade="all", labels="points"),
         why="Crates 11 and 12 no longer trade. At Q = 10 buyers value a crate at $10 and it costs $7: "
             "½ × 2 × ($10 − $7) = $3. Check: $108 − ($50 + $55) = $3."),
    dict(id="floor_loose", kind="control", market=_M,
         text="Instead, suppose the state sets the minimum price at $6 per crate. What happens?",
         options=["Nothing: price stays $8 and 12 crates trade", "Surplus of 4 crates",
                  "Shortage of 6 crates", "Price falls to the $6 floor"],
         answer=0, num=dict(control=("floor", 6), shade="all", labels="points"),
         why="A floor below the equilibrium price doesn't bind. The market still clears at $8."),
]



def _rotate_options(sc: dict) -> None:
    """The numeric questions above list the right answer first, for easy editing.
    Rotate each one by a fixed offset so the answer key isn't always A."""
    n = len(sc["options"])
    k = sum(map(ord, sc["id"])) % n
    sc["options"] = sc["options"][k:] + sc["options"][:k]
    sc["answer"] = (sc["answer"] - k) % n


for _s in SCENARIOS:
    if "num" in _s:
        _rotate_options(_s)

SCENARIO_BY_ID = {s["id"]: s for s in SCENARIOS}

# Light sanity check so a typo in an edit fails loudly at import time.
for _s in SCENARIOS:
    assert 0 <= _s["answer"] < len(_s["options"]), _s["id"]
    assert _s["kind"] in KIND_LABELS, _s["id"]
assert len(SCENARIO_BY_ID) == len(SCENARIOS), "duplicate scenario id"
