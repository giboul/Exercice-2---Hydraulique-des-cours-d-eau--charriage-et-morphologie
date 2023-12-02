from matplotlib import pyplot as plt
import numpy as np
plt.style.use("ggplot")


Q = 750
rhos = 2650
rhow = 1000
s = rhos/rhow
dm = 2.8/100
g = 9.81
J = 0.12/100

def Qs(Q, dm, s): return Q / ((s-1)*g)**0.5/dm**2.5

def yalin(Q, dm): return 1.5*Q**0.5/dm**0.25

def parker(Q, dm, s): return 4.4*Qs(Q, dm, s)**0.5*dm

def ashmore(Q, J, dm): return 0.0098*(rhow*g*Q*J)**0.777/dm**0.7

def millar(Q, dm, J, s, mu): return 16.5*Qs(Q, dm, s)**0.7*J**0.6*mu**-1.1*dm

plt.figure(figsize=(7, 4))
plt.axline((Q, 0), slope=float('inf'), ls='-.', label=f"$Q={Q}$ m$^3$/s", color='k', lw=1)
Q = np.linspace(0, 1.5*Q, num=1000)
plt.plot(Q, yalin(Q, dm), label="Érosion primaire selon Yalin")
plt.plot(Q, parker(Q, dm, s), label="Érosion primaire selon Parker")
plt.plot(Q, ashmore(Q, J, dm), label="Érosion secondaire selon Ashmore")
plt.plot(Q, millar(Q, dm, J, s, 1.7), label="Érosion secondaire selon Millar")
plt.legend(title=f"${s=:.1f}$  $J=${J:.2%}  $d_m={dm*100}$ cm", loc="upper left")
plt.xlabel("$Q$ [m$^3$/s]")
plt.ylabel("$L_{{nat}}$ [m]")
plt.tight_layout()
plt.savefig("figures/Q4/Lnat-OFEV.pdf", bbox_inches="tight")
plt.show()
