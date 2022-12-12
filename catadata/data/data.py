import pandas as pd
import geopandas as gpd
import pathlib
import os
import logging
import yaml

LOGGER = logging.getLogger()

dir_path = os.path.dirname(os.path.realpath(__file__))
LOGGER.error(dir_path)

cata_data_path = pathlib.Path(f"{dir_path}/Cata_data.csv")
cata_parcels_path = pathlib.Path(f"{dir_path}/100m Riparian Zone.shp")
cata_conservation_path = pathlib.Path(f"{dir_path}/cata_conservation.csv")

cata_data = pd.read_csv(cata_data_path.resolve(), dtype={"fid": int, "ALTPARNO": str})
cata_parcels = gpd.read_file(cata_parcels_path.resolve(), dtype={"fid": str, "ALTPARNO": str})


def get_cata_data():
    with open("./config.yaml") as fp:
        config = yaml.load(fp, Loader=yaml.FullLoader)

    conservation = pd.read_csv(cata_conservation_path.resolve(), dtype={"fid": int})
    cata_data = pd.read_csv(cata_data_path.resolve(), dtype={"fid": int, "ALTPARNO": str})

    cata_data = cata_data.join(conservation.set_index("fid")[config["conservation_columns"]], on="fid")

    print(cata_data.head())

    return cata_data


def get_fresh_cata_data():
    return pd.read_csv(cata_data_path.resolve(), dtype={"fid": int, "ALTPARNO": str})


def get_cata_parcels():
    cata_parcels.fid = cata_parcels.fid.apply(lambda d: str(int(d)))
    cata_parcels.to_crs(epsg=4326, inplace=True)
    return cata_parcels
