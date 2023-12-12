import pandas as pd
from hydrogibs.fluvial.profile import Profile
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
    profilename = profile
    profile = Profile(
        df['Dist. cumulée [m]'],
        df['Altitude [m s.m.]'],
        K, Js
    )

    fig = plt.figure(figsize=(9, 5))
    fig, (ax1, ax2) = profile.plot(fig=fig)
    ax1.plot(df['Dist. cumulée [m]'],
             df['Altitude [m s.m.]'],
             '-o', ms=8, c='gray', zorder=0,
             lw=3, label="Profil complet")
    # showing an example of a water depth
    zthres = 6.2 + profile.z.min()
    mask = profile.z <= zthres
    ax1.fill_between(profile.x[mask], profile.z[mask], zthres,
                     color='b', alpha=0.3, label="Exemple")

    # Pour faire plus joli
    l1, l2 = ax1.get_lines()
    hc, he = ax2.get_lines()
    ax2.dataLim.x1 = 1600  # ~xlim
    ax2.autoscale_view()
    ax1.set_title(profilename, loc='left', alpha=0.8)  # nom de la profile
    # legend
    lines = (l1, l2, he, hc)
    labels = [line.get_label() for line in lines]
    if profilename == 'Rhone18.846':
        ax1.legend(lines, labels, framealpha=0.8, ncols=2)
    else:
        ax1.get_legend().remove()

    plt.tight_layout()
    plt.savefig(f"figures/Q1/{profilename}_diagram.pdf", bbox_inches='tight')
    plt.show()

    # Interpolation de données plus précises (modèle trapézoïdal)
    h = np.linspace(profile.h.min(), profile.h.max(), num=1000)
    S = profile.interp_S(h)
    P = profile.interp_P(h)
    Q = profile.interp_Q(h)
