import numpy as np
import pandas as pd

RANDOM_STATE = 22
NUM_PLAYERS = 200
NUM_ROUNDS = 3
OUTPUT_CSV = "synthetic_player_data.csv"

np.random.seed(RANDOM_STATE)

def generate_player_round(player_skill, noise_scale=1.0):
    shots_fired = max(1, int(np.random.normal(20 + 5 * player_skill, 3)))
    hit_prob = np.clip(0.2 + 0.15 * player_skill, 0.05, 0.98)
    shots_hit = np.random.binomial(shots_fired, hit_prob)
    reaction_time = max(80, np.random.normal(300 - 30 * player_skill, 60))
    return shots_hit, shots_fired, reaction_time

# Generate data for all players
players = []

for i in range(NUM_PLAYERS):
    skill = np.clip(np.random.normal(0.0, 1.0) + np.random.choice([0, 1, -1], p=[0.6, 0.2, 0.2]), -2, 2)
    rounds = [generate_player_round(skill) for _ in range(NUM_ROUNDS)]
    shots_hit = np.array([r[0] for r in rounds])
    shots_fired = np.array([r[1] for r in rounds])
    reac = np.array([r[2] for r in rounds])

    total_hits = shots_hit.sum()
    total_shots = shots_fired.sum()
    accuracy = total_hits / total_shots if total_shots > 0 else 0.0
    avg_reaction = reac.mean()

    var_accuracy = np.var(shots_hit / np.maximum(shots_fired, 1))
    var_reaction = np.var(reac)
    var_hits = np.var(shots_hit)
    var_shots = np.var(shots_fired)

    players.append({
        'player_id': f"Player_{i:03d}",
        'shots_hit': total_hits,
        'shots_fired': total_shots,
        'accuracy': accuracy,
        'avg_reaction_ms': avg_reaction,
        'var_accuracy': var_accuracy,
        'var_reaction_ms': var_reaction,
        'var_shots_hit': var_hits,
        'var_shots_fired': var_shots,
        'skill': skill  #Random generated rank in order to keep all features correlated
    })

df = pd.DataFrame(players)


# Save to CSV
df.to_csv(OUTPUT_CSV, index=False)
print(f"Synthetic dataset generated: {OUTPUT_CSV}")
print(df.head())
