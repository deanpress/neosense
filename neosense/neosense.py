from boa.blockchain.vm.Neo.Runtime import CheckWitness
from boa.blockchain.vm.Neo.Blockchain import GetHeight
from boa.blockchain.vm.Neo.Storage import GetContext, Put, Delete, Get
from boa.code.builtins import concat
from .serialize import *
from .utils import is_owner
from boa.code.builtins import list


def register_product(args):
    """
    :param args:
        args[0]: senderhash
        args[1]: product id (something unique)
        args[2]: description (human readable description of the product, keep as short as possible to keep gas price as
                 low as possible)
        args[3]: max_license_number; set to False if you want to allow unlimited registrations
        args[4]: make transferable; set to True to allow users to exchange licenses themselves
        args[5]: product_expiration; blockheight at which the product is expired (no more licences will be distributed)
        args[6]: license_expiration; number of blocks for which a license is valid (set to True to make it valid for the
                                     duration of the product)
    :return: bool
    """

    product_id = args[1]
    product_exists = Get(GetContext, product_id)
    product_data = list(length=8)

    product_data[0] = args[0]
    product_data[2] = args[2]
    product_data[3] = args[3]
    product_data[4] = args[4]
    product_data[5] = args[5]
    product_data[6] = args[6]
    product_data[7] = 0

    if not product_exists:
        serialized_product_data = serialize_array(args)
        Put(GetContext, product_id, serialized_product_data)
        print("product registered")
        return True
    else:
        print("product already exists")
        return


def license_product(args):
    """
    Grant a license for a specific product, can only be called by the product owner:
    :param args:
        args[0]: product_id
        args[1]: user_id (user public key)

    :return: bool
    """
    product_id = args[0]

    if not is_owner(product_id):
        return False

    product = get_product(product_id)

    height = GetHeight()
    product_expiration = product[5]

    # check if the product can still be licensed
    if height > product_expiration:
        print('This product cannot be licensed anymore, it has expired')
        return False

    # check if there are still licenses available
    max_license_number = product[3]
    current_licenses = product[7]

    if current_licenses == max_license_number:
        print('licenses have been sold out!')
        return False

    user_id = args[1]
    license = concat(product_id, user_id)

    # block height at which the license expires
    license_expiration = height + product_expiration

    license_data = list(length=3)

    license_data[0] = user_id
    license_data[1] = license_expiration
    license_data[2] = product_id

    Put(GetContext, license, license_data)
    cln = increment_cln(product_id)
    return True


def get_product(product_id):
    """
    :param product_id:
    :return: deserialized list of product data
        [0]: owner of product (sender hash)
        [1]: product_id
        [2]: description
        [3]: max_license_number
        [4]: transferable
        [5]: product_expiration
        [6]: license_expiration
        [7]: current_license_number
    """
    serialized_product_data = Get(GetContext, product_id)
    unserialized_product_data = deserialize_bytearray(serialized_product_data)

    return unserialized_product_data


def increment_cln(product_id):
    """

    :param product_id:
    :return: bool
    """
    if not is_owner(product_id):
        return False

    product_data = get_product(product_id)

    # increment the cln
    current_cln = product_data[7]
    new_cln = current_cln + 1
    product_data[7] = new_cln

    Delete(GetContext, product_id)
    Put(GetContext, product_id, product_data)
    return True


def get_license(license_id):
    """
    Get the deserialized data of a license

    :param license_id:
    :return: list:
        [0]: owner (user_id)
        [1]: license_expiration
        [2]: product_id
    """
    serialized_license_data = Get(GetContext, license_id)
    license_data = deserialize_bytearray(serialized_license_data)

    return license_data


def transfer_license(license_id, new_owner):
    """
    transfer license from one user to the other

    :param license_id:
    :param new_owner:
    :return: bool
    """
    if not is_owner(license_id):
        return False

    license = get_license(license_id)
    product_id = license_id[2]
    product_data = get_product(product_id)
    transferable = product_data[4]

    # check if the license is still valid
    license_expiration_height = license[1]
    height = GetHeight()

    if height > license_expiration_height:
        print("This license has already expired!")
        return False

    if not transferable:
        print("This product does not support transfers")
        return False

    Delete(GetContext, license_id)
    license[0] = new_owner
    Put(GetContext, license_id, license)


def Main(operation, args):
    """
    The body of the contract, all operation go through here.

    :param operation:
        RegisterProduct :param args: see register_product
        :return: bool

        LicenseProduct :param args: see license_product
        :return: bool

        TransferLicense :param args: see transfer_license
        :return: bool

        GetLicenseInfo: :param args: [license_id]
        :return: list

        GetProductInfo: :param args: [product_id]
        :return: list
    """
    if operation == "RegisterProduct":
        return register_product(args)

    if operation == "LicenseProduct":
        return license_product(args)

    if operation == "TransferLicense":
        license_id = args[0]
        new_owner = args[1]
        return transfer_license(license_id, new_owner)

    if operation == "GetLicenseInfo":
        license_id = args[0]
        return get_license(license_id)

    if operation == "GetProductInfo":
        product_id = args[0]
        return get_product(product_id)
