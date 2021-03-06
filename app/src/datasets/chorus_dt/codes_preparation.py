"""
Get a raw dataset with gps coordinates and push dump it into a dictionnary with format:
dict(
    column_name -> dict(
        code -> value
    )
)
Each of these dictionnary must have a 'lat' and a 'lon' column (latitude, longitude).

So, if you want to check the coordinates of the city with postal code 75014, you can get them using:
    ```
    import dill

    with open('data/prepared/insee_codes.pkl', 'rb') as file_id:
        postal_codes = dill.load(file_id)
    lat = postal_codes['lat']['75114']
    lon = postal_codes['lon']['75114']
    print(lat, lon)
    ```
All of the output files are put into the /data/prepared folder
"""
import os
import dill
import pandas as pd

RAW_DATA_PATH = "/data/raw/chorus-dt"
PREPARED_DATA_PATH = "/data/prepared"


def prepare_insee():
    """
    Prepare the postal codes to gps coordinates data using laposte dataset available here:
    here: https://www.data.gouv.fr/en/datasets/base-officielle-des-codes-postaux/
    """
    insee_geocode = pd.read_csv(os.path.join(RAW_DATA_PATH, "laposte_hexasmal.csv"), delimiter=";")
    insee_geocode = insee_geocode.set_index("Code_commune_INSEE").dropna(subset=["coordonnees_gps"])
    insee_geocode[["lat", "lon"]] = insee_geocode["coordonnees_gps"].str.split(",", expand=True)
    insee_geocode = insee_geocode.to_dict()
    with open(os.path.join(PREPARED_DATA_PATH, "insee_codes.pkl"), "wb") as file_id:
        dill.dump(insee_geocode, file_id)


def prepare_uic():
    """
    Prepare the UIC codes using data available here : https://ressources.data.sncf.com/explore/dataset/liste-des-gares/table/
    The UIC codes in the chorus dump are truncated UIC codes.
    """
    stations_list = pd.read_csv(os.path.join(RAW_DATA_PATH, "liste-des-gares.csv"), delimiter=";")
    stations_list["truncated_code_uic"] = stations_list["CODE_UIC"].apply(lambda x: int(str(x)[:-1]))
    stations_list = stations_list.set_index("truncated_code_uic").dropna(subset=["C_GEO"])
    stations_list.rename(columns={"X_WGS84": "lon", "Y_WGS84": "lat"}, inplace=True)
    stations_list = stations_list.to_dict()
    with open(os.path.join(PREPARED_DATA_PATH, "uic_codes.pkl"), "wb") as file_id:
        dill.dump(stations_list, file_id)


def prepare_tvs():
    """
    Get the TVS codes available here:
    https://ressources.data.sncf.com/explore/dataset/referentiel-gares-voyageurs

    This is not use right now as it seems the chorus dump is not very well filled, for example, we have this kind of rows:
        TR_FRECO - Quimperle
    But ECO is the TVS code of Écommoy, and the TVS code of Quimplerle is QPL
    """
    tvs_codes = pd.read_csv(os.path.join(RAW_DATA_PATH, "referentiel-gares-voyageurs.csv"), delimiter=";")
    tvs_codes = tvs_codes.dropna(subset=["TVS", "WGS 84"])
    tvs_codes["extended_TVS"] = "TR_FR" + tvs_codes["TVS"]
    tvs_codes = tvs_codes.set_index("extended_TVS")
    tvs_codes[["lat", "lon"]] = tvs_codes["WGS 84"].str.split(",", expand=True)
    tvs_codes = tvs_codes.to_dict()
    with open(os.path.join(PREPARED_DATA_PATH, "tvs_codes.pkl"), "wb") as file_id:
        dill.dump(tvs_codes, file_id)


def prepare_iata():
    """
    Get the IATA codes available here:
    'https://ourairports.com/data/airports.csv'

    Some IATA coded-airports lack geocoding info

    """

    iata_codes = pd.read_csv(os.path.join(RAW_DATA_PATH, "airports.csv")).set_index("iata_code")
    iata_codes = iata_codes.loc[~iata_codes.latitude_deg.isna() & ~iata_codes.longitude_deg.isna()]
    iata_codes[["lat", "lon"]] = iata_codes[["latitude_deg", "longitude_deg"]]
    iata_codes = iata_codes.to_dict()

    with open(os.path.join(PREPARED_DATA_PATH, "iata_codes.pkl"), "wb") as file_id:
        dill.dump(iata_codes, file_id)


def main():
    prepare_uic()
    prepare_insee()
    prepare_tvs()
    prepare_iata()


if __name__ == "__main__":
    main()
