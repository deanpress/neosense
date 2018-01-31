from boa.blockchain.vm.Neo.Blockchain import GetHeight
from boa.blockchain.vm.Neo.Storage import GetContext, Put, Delete, Get
from helpers.serialize import *
from helpers.utils import is_owner
from boa.code.builtins import list
from neosense.product import init_product
from neosense.license import init_license


def register_product(args):
    """
    :param args:
        args[0]: senderhash
        args[1]: product id (something unique)
        args[2]: description (human readable description of the product, keep as short as possible to keep gas price as
                 low as possible)
        args[3]: max_license_number;
        args[4]: make transferable;
        args[5]: product_expiration; blockheight at which the product is expired (no more licences will be distributed)
        args[6]: license_expiration; number of blocks for which a license is valid

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
    # unpacking args
    product_id = args[0]
    user_id = args[1]

    if not is_owner(product_id):
        return False

    product = init_product(product_id)

    height = GetHeight()
    product_expiration = product.pe

    # check if the product can still be licensed
    if height > product_expiration:
        print('This product cannot be licensed anymore, it has expired')
        return False

    # check if there are still licenses available
    max_license_number = product.mln
    current_licenses = product.cln

    if current_licenses == max_license_number:
        print('licenses have been sold out!')
        return False

    license = concat(product_id, user_id)

    # block height at which the license expires
    license_duration = product.le
    license_expiration = height + license_duration

    license_data = list(length=3)

    license_data[0] = user_id
    license_data[1] = license_expiration
    license_data[2] = product_id

    Put(GetContext, license, license_data)
    cln = increment_cln(product_id)

    return True


def increment_cln(product_id):
    """
    :param product_id:
    :return: bool
    """
    if not is_owner(product_id):
        return False

    product = init_product(product_id)
    product_data = product.all
    # increment the cln
    current_cln = product.cln
    new_cln = current_cln + 1
    product_data[7] = new_cln

    Delete(GetContext, product_id)
    Put(GetContext, product_id, product_data)
    return True


def transfer_license(license_id, new_owner):
    """
    transfer license from one user to the other

    :param license_id:
    :param new_owner:
    :return: bool
    """
    if not is_owner(license_id):
        return False

    license = init_license(license_id)
    license_data = license.all
    product_id = license.product_id
    product = init_product(product_id)
    transferable = product.trans

    # check if the license is still valid
    license_expiration_height = license.expir
    height = GetHeight()

    if height > license_expiration_height:
        print("This license has already expired!")
        return False

    if not transferable:
        print("This product does not support transfers")
        return False

    Delete(GetContext, license_id)
    license_data[0] = new_owner
    Put(GetContext, license_id, license)
    return True


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
        license = init_license(license_id)
        return license.all

    if operation == "GetProductInfo":
        product_id = args[0]
        product = init_product(product_id)
        return product.all
