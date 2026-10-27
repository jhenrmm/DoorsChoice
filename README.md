# DoorsChoice

A simulation of the **Monty Hall problem**: three doors, one car, two goats, and one very important decision — **keep your door or switch?**

The program plays the game hundreds of thousands of times under both strategies and shows which one wins more often, then cross-checks the result with an exact mathematical enumeration.

## The game

1. There are **3 doors**. Behind one is a car; behind the other two are goats.
2. You pick a door.
3. The host, who knows where the car is, opens one of the two remaining doors and always reveals a **goat**.
4. Two doors stay closed: your pick and the only other unopened door. You may **keep** your door or **switch**.

Which choice wins more often?

## The math

| Your first pick | Probability | Host opens | Staying wins | Switching wins |
| --- | --- | --- | --- | --- |
| Correct (car) | 1/3 | one of the two goat doors | yes | no |
| Wrong (goat) | 2/3 | the other goat door | no | yes |

- **Stay:** wins only when your first pick was correct → **1/3 ≈ 33.3%**
- **Switch:** wins whenever your first pick was wrong → **2/3 ≈ 66.7%**

Switching doubles your chance. The host's reveal is not random noise: because he can never show the car, the 2/3 probability that your first pick was wrong collapses onto the single remaining unopened door.

## Results

Real output from `python main.py` (100,000 rounds per strategy):

```text
Monte-Carlo simulation - 100,000 rounds per strategy
(seed = 2026)

strategy        wins    losses   win rate   95% interval
--------------------------------------------------------------
stay          33,195    66,805    33.20%   [32.90%, 33.49%]
switch        66,680    33,320    66.68%   [66.39%, 66.97%]

Exact answer from full enumeration:
  stay    P(win) =    1/3  = 33.3%
  switch  P(win) =    2/3  = 66.7%

Conclusion: switching wins 2/3 of the time, staying wins 1/3.
You should always switch.
```

The simulated rates land on the theoretical values inside their 95% confidence intervals.

## Getting started

Requires **Python 3.8+** and has **no dependencies** — the standard library is enough.

```bash
git clone https://github.com/jhenrmm/DoorsChoice.git
cd DoorsChoice
python main.py
```

### Options

| Command | Description |
| --- | --- |
| `python main.py` | Simulate 100,000 rounds per strategy |
| `python main.py --rounds 1000000` | Larger sample for a tighter interval |
| `python main.py --seed 42` | Reproducible run (default seed: `2026`) |
| `python main.py --seed 0` | Use a random seed |
| `python main.py --play` | Play the game yourself in the terminal |

### Play interactively

```bash
python main.py --play
```

```text
Round 1: doors are 1, 2, 3.
Pick a door (1-3) [default 2]: 1
The host opens door 3: a goat.
Keep door 1 (k) or switch to door 2 (s)? s
Door 2 hides the car. You chose to switch and picked door 2 - you WIN!
Score: stay 0/0, switch 1/1
```

Press `Ctrl+C` to stop.

## How it works

- **`simulate()`** plays many independent games. In every game the prize and the player's first choice are random, and the host picks uniformly at random from the goat doors that are not the player's door.
- **`exact_probabilities()`** enumerates every possible game exactly. Each game is weighted by its true probability; when both remaining doors hide goats the host's 50/50 split is accounted for. Skipping that detail is the classic bug that makes an enumeration wrongly report 50/50.
- **`wilson_interval()`** reports a 95% Wilson score interval, a proportion interval that behaves well for any sample size.

## Project structure

```text
DoorsChoice/
├── main.py        # simulation, exact enumeration, and interactive mode
├── README.md
└── .gitignore
```

## License

No license has been specified for this repository.
