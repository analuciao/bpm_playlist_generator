import matplotlib.pyplot as plt

def plot_bpm_histogram(songs_df, bpm_col='bpm', out_path='bpm_histogram.png'):
    bpm = songs_df[bpm_col].dropna().astype(float)

    plt.figure(figsize=(8, 5))            # width x height in inches
    n, bins, patches = plt.hist(bpm, bins=10, edgecolor='black', alpha=0.75)
    plt.xlabel('BPM', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.title('Distribution of Song BPMs', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()

    # save high-resolution image suitable for posters
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    from bpm_binner import songs  # or however you import songs
    plot_bpm_histogram(songs, out_path="bpm_histogram.png")
    bin_edges = [80, 110, 140, 170, 1000]
    plt.show()
    print("Saved bpm_histogram.png")