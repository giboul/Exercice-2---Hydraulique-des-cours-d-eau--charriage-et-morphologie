import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from hydrogibs.fluvial.profile import Profile
from scipy.interpolate import interp1d
plt.style.use('ggplot')


INPUT_FILE = (
    '2023_CIVIL-410_Exercice2_'
    'Biblio_hydraulique_Profils_Rhone_et_Shields.xlsm'
)
PROFILES = ('Rhone18.846', 'Rhone18.947')
USECOLS = 'H:K'
GMS = (33, 32)
SLOPES = (0.12/100, 0.13/100)

theta_cr = 0.05
s = 2.65
Dm = 2.7535714285714286 / 100

month, Qmonth = pd.read_csv("data/Débits mensuels - Porte du Scex.csv", skiprows=1).to_numpy().T
Qmonth = np.asarray(Qmonth, dtype=float)


def smart_jaeggi(h, i):
    return 4.2/(s - 1) * i**1.6 * (1 - theta_cr*(s-1)*Dm/h/i)


profiles = []
for profile, K, slope in zip(PROFILES, GMS, SLOPES):

    section = pd.read_excel(INPUT_FILE, sheet_name=profile, usecols=USECOLS, dtype=float)
    section = Profile(
        section['Dist. cumulée [m]'],
        section['Altitude [m s.m.]'],
        K,
        slope
    )

    profiles.append(section.df.query('Q < 1600').sort_values('h'))

fig, ax = plt.subplots(figsize=(5, 3))
for df, profile, K, slope in zip(profiles, PROFILES, GMS, SLOPES):

    h = np.linspace(df.h.min(), df.h.max(), num=10000)
    Q = section.interp_Q(h)

    Qs = Q * smart_jaeggi(h, slope)
    Qs[Qs < 0] = 0
    ax.plot(Q, Qs, '-.', label=profile)

ax.set_xlabel('Q$_L$ [m$^3$/s]')
ax.set_ylabel('Q$_S$ [m$^3$/s]')
ax.legend()
# ax.dataLim.x1 = 1600
# ax.autoscale_view()
plt.tight_layout()
plt.savefig("figures/Q3/smart.pdf", bbox_inches='tight')
plt.show()


# Débits solides
zorder=2
for df, profile, K, slope in zip(profiles, PROFILES, GMS, SLOPES):

    hmensuels = interp1d(df.Q, df.h)(Qmonth)

    Qsmensuels = Qmonth * np.maximum(smart_jaeggi(hmensuels, slope), 0)
    Vs = Qsmensuels.sum()*30*24*3600

    plt.bar(month, Qsmensuels, label=f"\n{profile}\n$V_{{annuel}}={Vs:.0e}$ m$^3$", zorder=zorder)
    zorder -= 1

plt.ylabel("$Q_S$ [m$^3$/s]")
plt.legend()
plt.tight_layout()
plt.savefig("figures/Q3/solides.pdf", bbox_inches='tight')
plt.show()
