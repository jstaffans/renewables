from functools import lru_cache
from pyiso import client_factory
import pandas as pd


@lru_cache()
def get_client(ba_name):
    return client_factory(ba_name)

def generation(ba_name, control_area, start, end):
    entso = get_client(ba_name)
    result = entso.get_generation(latest=True, control_area=control_area, start_at=start, end_at=end)
    df = pd.DataFrame(result)
    return df
