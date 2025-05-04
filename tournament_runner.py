#!/usr/bin/env python3
import subprocess
import re
import sys
import argparse


def parse_scores(block: str):
    b = re.findall(r"Black Score:\s*(\d+)", block)
    w = re.findall(r"White Score:\s*(\d+)", block)
    if not b or not w:
        raise ValueError("Scores not found in block:\n" + block[-200:])
    return int(b[-1]), int(w[-1])


def run_tournament(echo: bool):
    # invoke your engine
    proc = subprocess.run(
        ["python3", "play.py", "Othello"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    out = proc.stdout

    if echo:
        print(out, end="", flush=True)

    # split into two games
    marker = "INFO: Game has terminated!"
    splits = [m.start() for m in re.finditer(marker, out)]
    if len(splits) != 2:
        raise RuntimeError(f"Expected 2 games, found {
                           len(splits)} terminations")
    blocks = []
    prev = 0
    for idx in splits:
        blocks.append(out[prev:idx])
        prev = idx + len(marker)

    # assignments: (black, white)
    assignments = [
        ("random_player", "my_player"),  # game1
        ("my_player",    "random_player")  # game2
    ]

    game_results = []  # list of winners for each game
    for i, blk in enumerate(blocks):
        b_score, w_score = parse_scores(blk)
        black_p, white_p = assignments[i]
        if w_score > b_score:
            game_results.append(white_p)
        elif b_score > w_score:
            game_results.append(black_p)
        else:
            game_results.append("draw")

    # determine tournament winner
    wins = {"my_player": game_results.count("my_player"),
            "random_player": game_results.count("random_player")}
    if wins["my_player"] > wins["random_player"]:
        tourney_winner = "my_player"
    elif wins["random_player"] > wins["my_player"]:
        tourney_winner = "random_player"
    else:
        tourney_winner = "draw"

    return game_results, tourney_winner


def main():
    p = argparse.ArgumentParser(
        description="Run Othello tournament multiple times and aggregate results"
    )
    p.add_argument("-n", "--runs", type=int, default=1,
                   help="number of tournament repetitions")
    p.add_argument("--no-echo", action="store_true",
                   help="don't print the raw tournament stdout")
    args = p.parse_args()

    total_game_wins = {"my_player": 0, "random_player": 0, "draw": 0}
    total_tourney_wins = {"my_player": 0, "random_player": 0, "draw": 0}

    for run in range(1, args.runs + 1):
        if args.runs > 1:
            print(f"\n=== Run {run}/{args.runs} ===")
        game_results, tourney_winner = run_tournament(echo=not args.no_echo)

        # tally
        for g in game_results:
            total_game_wins[g] += 1
        total_tourney_wins[tourney_winner] += 1

        # per-run summary
        if args.runs > 1:
            print("  Game results:", game_results)
            print("  Tournament winner:", tourney_winner)

    # final aggregate summary
    print("\n=== Aggregate Summary ===")
    print(f"Total runs: {args.runs}")
    print("Game wins:")
    print(f"  my_player:    {total_game_wins['my_player']}")
    print(f"  random_player:{total_game_wins['random_player']}")
    print(f"  draws:        {total_game_wins['draw']}")
    print("Tournament wins:")
    print(f"  my_player:    {total_tourney_wins['my_player']}")
    print(f"  random_player:{total_tourney_wins['random_player']}")
    print(f"  draws:        {total_tourney_wins['draw']}")


if __name__ == "__main__":
    main()
