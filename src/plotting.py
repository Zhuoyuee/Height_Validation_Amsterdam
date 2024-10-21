import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv(r'C:\Users\www\PycharmProjects\Height_Ams\data\result_3dglobpf.csv')

bins = np.arange(-26.6, 9.85 + 0.76, 0.76)

# Step 3: Cut the "Avg Height Diff" data into the new bins
df['binned'] = pd.cut(df['Avg Height Diff'], bins=bins, right=False)

# Step 4: Count the frequency of each bin
bin_counts = df['binned'].value_counts(sort=False)

# Step 5: Plot the histogram with the updated binning
plt.figure(figsize=(10, 6))
bin_counts.plot(kind='bar', color='skyblue')

plt.title('Distribution of Building Height Differences for 3DGloBPF', fontsize=14)
plt.xlabel('Height Difference (meters)', fontsize=12)
plt.ylabel('Number of Buildings', fontsize=12)
plt.xticks(rotation=45)

plt.xticks(ticks=np.arange(0, len(bins), 2), labels=[f'{bins[i]:.1f}' for i in range(0, len(bins), 2)], rotation=45)

plt.tight_layout()
plt.show()