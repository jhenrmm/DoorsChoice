"""Monty Hall problem: should you keep your door or switch?

The game
--------
1. There are 3 doors. Behind one is a car, behind the other two are goats.
2. You pick a door (the "first choice"). You do not open it yet.
3. The host knows where the car is and opens one of the two remaining doors,
   always revealing a goat.
4. Two doors stay closed: your first choice and the only other unopened door.
   The host asks: keep your door, or switch to the other one?

The question
------------
Which strategy wins the car more often: STAY or SWITCH?

Exact answer
------------
* If your first choice was right (probability 1/3), staying wins and switching loses.
* If your first choice was wrong (probability 2/3), the host is forced to leave the
  car behind the only other unopened door, so switching wins and staying loses.

Therefore:  P(win | stay) = 1/3   and   P(win | switch) = 2/3.
Switching doubles your chance of winning.

This script checks that result two ways: a Monte-Carlo simulation, and an
exact enumeration of every possible game. It also lets you play by hand.

Usage
-----
    python main.py                 # simulate 100,000 rounds per strategy
    python main.py --rounds 1000000
    python main.py --play          # play the game yourself
"""

from __future__ import annotations

import argparse
import math
import random
import sys
from collections import Counter
from fractions import Fraction
from itertools import product

DOORS = (0, 1, 2)
STRATEGIES = ("stay", "switch")


def play_round(strategy: str, prize: int, first_choice: int, host_pick: int) -> bool:
    """Resolve one round with every random decision already made.

    `host_pick` is a door the host is allowed to open: it is not the player's
    door and it does not hide the prize. Returns True if the player wins.
    """
    other_closed = [d for d in DOORS if d != first_choice and d != host_pick][0]

    if strategy == "stay":
        final_choice = first_choice
    elif strategy == "switch":
        final_choice = other_closed
    else:
        raise ValueError(f"unknown strategy: {strategy!r}")

    return final_choice == prize


def simulate(rounds: int, strategy: str, rng: random.Random) -> int:
    """Play `rounds` games with the given strategy and return the number of wins."""
    wins = 0
    for _ in range(rounds):
        prize = rng.choice(DOORS)
        first_choice = rng.choice(DOORS)

        # The host opens a goat door that is not the player's door.
        # (There is always at least one such door.)
        host_options = [d for d in DOORS if d != first_choice and d != prize]
        host_pick = rng.choice(host_options)

        wins += play_round(strategy, prize, first_choice, host_pick)
    return wins


def exact_probabilities() -> dict[str, Fraction]:
    """Enumerate every distinct game (prize, first choice, host choice).

    Each game is weighted by its true probability. The prize and the first
    choice are each uniform (1/3, 1/3). The host choice matters: when both
    remaining doors hide goats the host opens one of them at random, so each
    of those two doors only gets half the weight. Ignoring that split is the
    classic reason the enumeration wrongly reports 50/50.
    """
    wins = {s: Fraction(0) for s in STRATEGIES}
    total = Fraction(0)

    for prize, first_choice in product(DOORS, repeat=2):
        host_options = [d for d in DOORS if d != first_choice and d != prize]
        weight = Fraction(1, len(DOORS) ** 2 * len(host_options))

        for host_pick in host_options:
            total += weight
            for strategy in STRATEGIES:
                if play_round(strategy, prize, first_choice, host_pick):
                    wins[strategy] += weight

    return {s: wins[s] / total for s in STRATEGIES}


def wilson_interval(wins: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for a proportion."""
    if n == 0:
        return (0.0, 0.0)
    p = wins / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def report_simulation(rounds: int, seed: int | None) -> None:
    rng = random.Random(seed)

    print(f"Monte-Carlo simulation - {rounds:,} rounds per strategy")
    if seed is not None:
        print(f"(seed = {seed})")
    print()
    print(f"{'strategy':<10}{'wins':>10}{'losses':>10}{'win rate':>11}   95% interval")
    print("-" * 62)

    for strategy in STRATEGIES:
        wins = simulate(rounds, strategy, rng)
        losses = rounds - wins
        rate = wins / rounds
        low, high = wilson_interval(wins, rounds)
        print(
            f"{strategy:<10}{wins:>10,}{losses:>10,}{rate:>10.2%}"
            f"   [{low:.2%}, {high:.2%}]"
        )

    print()
    print("Exact answer from full enumeration:")
    for strategy, p in exact_probabilities().items():
        print(f"  {strategy:<7} P(win) = {str(p):>6}  = {float(p):.1%}")

    print()
    print("Conclusion: switching wins 2/3 of the time, staying wins 1/3.")
    print("You should always switch.")


def play_interactive() -> None:
    """Play the game yourself, one round at a time."""
    rng = random.Random()
    wins = Counter()
    games = Counter()

    print("Monty Hall - interactive mode. Press Ctrl+C to stop.\n")

    try:
        while True:
            prize = rng.choice(DOORS)
            first_choice = rng.choice(DOORS)

            print(f"Round {sum(games.values()) + 1}: doors are 1, 2, 3.")
            raw = input(f"Pick a door (1-3) [default {first_choice + 1}]: ").strip()
            if raw:
                if raw not in {"1", "2", "3"}:
                    print("Please enter 1, 2 or 3.\n")
                    continue
                first_choice = int(raw) - 1

            # Host opens a goat door that is not the player's door. If both of the
            # other doors are goats the host picks one at random.
            host_options = [d for d in DOORS if d != first_choice and d != prize]
            host_pick = rng.choice(host_options)
            other_closed = [d for d in DOORS if d != first_choice and d != host_pick][0]

            print(f"The host opens door {host_pick + 1}: a goat.")

            answer = ""
            while answer not in {"s", "k"}:
                answer = (
                    input(
                        f"Keep door {first_choice + 1} (k) or switch to "
                        f"door {other_closed + 1} (s)? "
                    )
                    .strip()
                    .lower()
                )

            strategy = "switch" if answer == "s" else "stay"
            final_choice = other_closed if strategy == "switch" else first_choice
            won = final_choice == prize

            games[strategy] += 1
            wins[strategy] += won

            print(f"Door {prize + 1} hides the car. You chose to {strategy} ", end="")
            print(f"and picked door {final_choice + 1} - you {'WIN' if won else 'LOSE'}!")
            print(
                f"Score: stay {wins['stay']}/{games['stay']}, "
                f"switch {wins['switch']}/{games['switch']}\n"
            )
    except (KeyboardInterrupt, EOFError):
        print("\n\nThanks for playing. The math still says: switch.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Monty Hall problem simulation")
    parser.add_argument(
        "--rounds",
        type=int,
        default=100_000,
        help="rounds to simulate per strategy (default: 100000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=2026,
        help="random seed for reproducible results (default: 2026, use 0 for random)",
    )
    parser.add_argument(
        "--play",
        action="store_true",
        help="play the game yourself instead of simulating",
    )
    args = parser.parse_args(argv)

    if args.play:
        play_interactive()
        return 0

    if args.rounds <= 0:
        parser.error("--rounds must be greater than 0")

    report_simulation(args.rounds, None if args.seed == 0 else args.seed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
