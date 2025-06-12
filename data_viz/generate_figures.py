import os
import sys
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from PIL import Image

data_dir = None
simu_id = None
figure_dir = None
i = 1
try:
    while i < len(sys.argv[i]):
        if sys.argv[i] == '-data_dir':
            data_dir = sys.argv[i+1]
        if sys.argv[i] == '-simu_id':
            simu_id = int(sys.argv[i+1])
        if sys.argv[i] == '-figure_dir':
            figure_dir = sys.argv[i+1]
        i += 2
except:
    pass

if data_dir is None or simu_id is None or figure_dir is None:
    print('Error: Missing argument')
    exit(1)

if data_dir[-1] != '/': data_dir += '/'
if figure_dir[-1] != '/': figure_dir += '/'
figure_dir += 'simu_%d/'%simu_id

if not os.path.exists(figure_dir):
    os.makedirs(figure_dir, exist_ok=True)

map_df = gpd.read_file('../src_data/us_county_mainland/us_county.shp')
data_fn = 'simu_%d_region_level.csv'
pop_fn = '../src_data/usa_%s_population.csv'
data_df = pd.read_csv(data_dir+data_fn%simu_id, dtype={'GeoId':str})

len_geoid = len(data_df.loc[0,'GeoId'])
if len_geoid == 5:
    region_level = 'county'
elif len_geoid == 11:
    region_level = 'census_tract'
else:
    region_level = 'cbg'

data_df['GeoId'] = data_df['GeoId']
data_df['Infected'] = data_df['Infectious'] + data_df['Recovered']
data_df = data_df.drop_duplicates(subset=['GeoId','Infected'])
data_df = data_df.groupby(['Day', 'GeoId']).sum().reset_index()

max_infected = data_df['Infected'].max()

pop_data = pd.read_csv(pop_fn%region_level, dtype={'GeoId':str})
pop_data['Infected-plot'] = 0
output_figures = []
for d in range(len(data_df['Day'].unique())):
    fig, ax = plt.subplots(figsize = (20,20))

    plot_data = pop_data.join(data_df[data_df['Day'] == d].set_index('GeoId')['Infected'], on = 'GeoId', how = 'left')
    plot_data['Infected'] = plot_data['Infected'].fillna(plot_data['Infected-plot'])
    pop_data['Infected-plot'] = plot_data['Infected']

    plot_data['GeoId'] = plot_data['GeoId'].apply(lambda x: x[:5])
    plot_data = plot_data.groupby('GeoId')[['Population','Infected']].sum().reset_index()
    prob_map_df = map_df.merge(plot_data, left_on='GEOID', right_on='GeoId', how = 'left').fillna(0)
    prob_map_df.plot(column='Infected', cmap='Blues',  edgecolor='#082657', ax = ax, linewidth = 0.1, legend=True , vmin=0, vmax=max_infected, legend_kwds={'shrink': 0.5, 'orientation':'horizontal'})
    ax.axis('off')
    ax.set_title(f'Day {d}', fontsize=16)

    fig_fn = '%s/Day%d.png'%(figure_dir,d)
    output_figures.append(fig_fn)
    fig.savefig(fig_fn, bbox_inches="tight")
    plt.close(fig)

gif_fn = figure_dir[:-1] + '.gif'
images = [Image.open(fig_fn) for fig_fn in output_figures]
images[0].save(
    gif_fn,
    save_all=True,
    append_images=images[1:],
    duration=200,
    loop=0
)