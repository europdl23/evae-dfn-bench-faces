# Training time, epochs, parameters, collapse flags and active slots per N_max variant -> outputs/run_summary.csv
import json, pandas as pd, numpy as np
from pathlib import Path
W = Path(__file__).resolve().parent; rows = []
for n in (50, 120, 200):
    for p in sorted((W / 'models' / ('N%d' % n)).glob('*/run_status.json')):
        j = json.load(open(p)); rows.append(dict(nmax=n, run=p.parent.name, elapsed_s=j['elapsed_s'], epochs=j['epochs'], n_params=j['n_params'],
                                                 best_val_loss=j['best_val_loss'], kl_spatial=j['kl_spatial'], kl_geometry=j['kl_geometry'], classification=j['classification']))
R = pd.DataFrame(rows); R.to_csv(W / 'outputs' / 'runs_per_model.csv', index=False)
A = pd.concat([pd.read_csv(W / 'outputs' / ('active_slots_N%d.csv' % n)) for n in (50, 120, 200)])
S = R.groupby('nmax').agg(models=('run', 'size'), params=('n_params', 'first'), train_s_mean=('elapsed_s', 'mean'), train_s_min=('elapsed_s', 'min'), train_s_max=('elapsed_s', 'max'),
                          epochs_mean=('epochs', 'mean'), s_per_epoch=('elapsed_s', lambda x: (x / R.loc[x.index, 'epochs']).mean()), stable=('classification', lambda x: (x == 'STABLE').sum()))
S = S.join(A.groupby('nmax').agg(active_slots_mean=('active_slots', 'mean'), active_slots_max=('active_slots', 'max'), traces_mean=('traces', 'mean'), traces_max=('traces', 'max')))
S.round(2).to_csv(W / 'outputs' / 'run_summary.csv'); print(S.round(2).to_string())
