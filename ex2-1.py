import pandas as pd
from hydrogibs.fluvial.canal import Section
from matplotlib import pyplot as plt
import numpy as np
plt.style.use('ggplot')


INPUT_FILE = (
    '2023_CIVIL-410_Exercice2_'
    'Biblio_hydraulique_Profils_Rhone_et_Shields.xlsm'
)
USECOLS = 'H:L'
PROFILES = ('Rhone18.846', 'Rhone18.947')
GMS = (33, 32)
SLOPES = (0.12/100, 0.13/100)


for profile, K, Js in zip(PROFILES, GMS, SLOPES):

    # read profile
    df = pd.read_excel(INPUT_FILE, sheet_name=profile,
                       usecols=USECOLS, dtype=float)
    # Initialisation de l'objet
    section = Section(
        df['Dist. cumulée [m]'],
        df['Altitude [m s.m.]'],
    ).compute_GMS_data(K, Js).compute_critical_data()

    # section.rawdata.to_csv(f'out/raw_{sheet}.csv', index=False)
    # section.data.to_csv(f'out/complete_{sheet}.csv', index=False)
    fig = plt.figure(figsize=(9, 5))
    fig, (ax1, ax2) = section.plot(h=6.35, show=False, fig=fig)

    # Pour faire plus joli
    lit, pts, eau, *_ = ax1.get_children()
    hc, he = ax2.get_lines()
    ax2.dataLim.x1 = 1600  # ~xlim
    ax2.autoscale_view()
    ax1.set_title(profile, loc='left', alpha=0.8)  # nom de la section
    # légende
    lines = (lit, pts, eau, he, hc)
    labels = [line.get_label() for line in lines]
    if profile == 'Rhone18.846':
        ax1.legend(lines, labels, framealpha=0.8, ncols=2)
    else:
        ax1.get_legend().remove()

    plt.tight_layout()
    plt.savefig(f"figures/Q1/{profile}_diagram.pdf", bbox_inches='tight')
    plt.show()

    # Interpolation de données plus précises (modèle trapézoïdal)
    h = np.linspace(section.h.min(), section.h.max(), num=1000)
    S = section.interp_S(h)
    P = section.interp_P(h)
    Q = section.interp_Q(h)
