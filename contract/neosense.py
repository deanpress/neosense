"""
NeoSense Smart Contract based Licensing
Created by Dean van Dugteren (City of Zion, VDT Network)
hello@dean.press
"""

from boa.blockchain.vm.Neo.Runtime import CheckWitness
from boa.blockchain.vm.Neo.Storage import GetContext, Put, Delete, Get
from boa.code.builtins import concat


def is_owner(product_id):
    """
    Verify that the product is owned by the requesting user.
    """
    print('Am I the product owner?')
    product_owner = Get(GetContext, product_id)
    is_product_owner = CheckWitness(product_owner)
    if not is_product_owner:
        print('Not the product owner!')
    return is_product_owner


# Main Operation
def Main(operation, args):
    """
    Main definition for the smart contracts

    :param operation: the operation to be performed
    :type operation: str

    :param args: list of arguments.
        args[0] is always sender script hash
        args[1] is always product_id
        args[2] (optional) is always another script hash
    :param type: str

    :return:
        byterarray: The result of the operation
    """

    # Common definitions
    user_hash = args[0]
    product_id = args[1]

    user_license = concat(user_hash, product_id)

    # Check if we are requesting licensing for the sender or a different user.
    if len(args) == 3:
        print('License for different user')
        requested_user = args[2]
        requested_license = concat(requested_user, product_id)
    else:
        print('License for me')
        requested_user = user_hash
        requested_license = user_license

    # check if a user is authorized
    if not CheckWitness(user_hash):
        print("Not Authorized")
        return False
    print("Authorized")

    # Every invocation of the contract requires an operation
    if not operation:
        print('Invalid Invocation, operation is missing.')
        return False

    # Registering a product
    if operation == 'RegisterProduct':
        print('RegisterProduct')
        product_exists = Get(GetContext, product_id)
        if not product_exists:
            Put(GetContext, product_id, user_hash)
            print("Product Registered")
            return True

    # Licensing a product
    if operation == 'LicenseProduct':
        print('LicenseProduct')

        if is_owner(product_id):
            # License the product
            Put(GetContext, requested_license, requested_user)
            print("Product Licensed")
            return True

    # Transferring a license
    if operation == 'TransferLicense':
        license_owner = Get(GetContext, user_license)

        if license_owner:
            print("License exists")
            is_license_owner = CheckWitness(license_owner)

            # Am I the license owner?
            if is_license_owner:
                print("User is License Owner")
                # Transfer License
                new_user_hash = args[2]
                new_license = concat(new_user_hash, product_id)
                Delete(GetContext, user_license)
                Put(GetContext, new_license, new_user_hash)
                print("License Transfered")
                return True

    # Remove a license
    if operation == 'RemoveLicense':

        # Am I the product owner?
        if is_owner(product_id):

            # Delete the license
            user_hash_to_del = args[2]
            license_to_del = concat(user_hash_to_del, product_id)
            Delete(GetContext, license_to_del)
            return True

    # Get the owner of a specific license
    if operation == 'GetLicense':
        print("GetLicense")
        requested_license = concat(requested_user, product_id)
        license_owner = Get(GetContext, requested_license)
        if license_owner:
            return license_owner

    print('Invalid operation provided.')
    return False
