from boa.blockchain.vm.Neo.Storage import GetContext, Get
from helpers.serialize import *


class License():
    owner = "a"
    expir = 1
    product_id = "a"


def init_license(license_id):

    serialized_license_data = Get(GetContext, license_id)
    license_data = deserialize_bytearray(serialized_license_data)

    license = License()

    license.owner = license_data[0]
    license.expir = license_data[1]
    license.product_id = license_data[2]
    license.all = license_data

    return license
