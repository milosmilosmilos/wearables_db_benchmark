import matplotlib.pyplot as plt


dataset_sizes = [1, 5, 10, 20, 50] 

latences = {
    r"$Q_{11}$":    [16.21, 33.81, 51.79, 81.91, 158.46],
    r"$Q_{12}$ ":  [24.87, 73.66, 130.86, 227.71, 543.22],
    r"$Q_{21}$ ":  [29.96, 60.69, 99.47, 184.93, 389.96],
    r"$Q_{22}$ ": [45.05, 134.32, 228.14, 435.83, 975.65],
}

relations = {
    r"$Q_{12}/Q_{11}$ (Wide shema)":   [1.53, 2.18, 2.53, 2.78, 3.43],
    r"$Q_{22}/Q_{21}$ (Narrow shema)": [1.50, 2.21, 2.29, 2.36, 2.50],
    r"$Q_{21}/Q_{11}$ (Upit bez konteksta)": [1.85, 1.80, 1.92, 2.26, 2.46],
    r"$Q_{22}/Q_{12}$ (Kontekstualni upit)": [1.81, 1.82, 1.74, 1.91, 1.80],
}

STYLES = [
    {"marker": "o", "linestyle": "-"},
    {"marker": "s", "linestyle": "--"},
    {"marker": "^", "linestyle": "-."},
    {"marker": "D", "linestyle": ":"},
]


def draw_image3():
    fig, ax = plt.subplots(figsize=(7, 5))

    for (naziv, vrednosti), stil in zip(latences.items(), STYLES):
        ax.plot(
            dataset_sizes,
            vrednosti,
            label=naziv,
            color="black",
            markerfacecolor="white",
            markersize=7,
            linewidth=1.5,
            **stil,
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(dataset_sizes)
    ax.set_xticklabels([f"{s}M" for s in dataset_sizes])

    ax.set_xlabel("Veličina polaznog skupa podataka (broj redova)")
    ax.set_ylabel("Vreme izvršavanja upita (ms, logaritamska skala)")
    ax.set_title("Apsolutno vreme izvršavanja upita u zavisnosti\n od veličine polaznog skupa podataka")
    ax.legend(loc="upper left", frameon=True)
    ax.grid(True, which="both", linestyle=":", linewidth=0.5, color="gray")

    fig.tight_layout()
    fig.savefig("slika3_apsolutna_latencija.png", dpi=400)
    print("Sacuvano: slika3_apsolutna_latencija.png")


def draw_image4():
    fig, ax = plt.subplots(figsize=(7, 5))

    for (naziv, vrednosti), stil in zip(relations.items(), STYLES):
        ax.plot(
            dataset_sizes,
            vrednosti,
            label=naziv,
            color="black",
            markerfacecolor="white",
            markersize=7,
            linewidth=1.5,
            **stil,
        )

    ax.set_xscale("log")
    ax.set_xticks(dataset_sizes)
    ax.set_xticklabels([f"{s}M" for s in dataset_sizes])

    ax.set_xlabel("Veličina polazng skupa podataka (broj redova)")
    ax.set_ylabel("Faktor uvećanja (x)")
    ax.set_title("Relativni relations vremena izvršavanja upita\n u zavisnosti od veličine polaznog skupa podataka")
    ax.legend(loc="upper left", frameon=True)
    ax.grid(True, which="both", linestyle=":", linewidth=0.5, color="gray")

    fig.tight_layout()
    fig.savefig("slika4_relativni_relations.png", dpi=400)
    print("Sacuvano: slika4_relativni_relations.png")


if __name__ == "__main__":
    draw_image3()
    draw_image4()
    print("Done.")