import pandas as pd
import geopandas as gpd
import pathlib

print(pathlib.Path(".").resolve())

cata_data_path = pathlib.Path("./catadata/data/cata_data.csv")
cata_parcels_path = pathlib.Path("./catadata/data/100m Riparian Zone.shp")

cata_data = pd.read_csv(cata_data_path.resolve(), dtype={"fid": int, "ALTPARNO": str})
cata_parcels = gpd.read_file(cata_parcels_path.resolve(), dtype={"fid": str, "ALTPARNO": str})


def get_cata_data():
    return cata_data


def get_cata_parcels():
    cata_parcels.fid = cata_parcels.fid.apply(lambda d: str(int(d)))
    cata_parcels.to_crs(epsg=4326, inplace=True)
    return cata_parcels
