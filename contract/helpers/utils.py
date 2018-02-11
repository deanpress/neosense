from boa.blockchain.vm.Neo.Runtime import CheckWitness
from boa.blockchain.vm.Neo.Storage import GetContext, Get


def is_owner(value):
    """
    Verify that the product or license is owned by the requesting user.
    """
    owner = Get(GetContext, value)
    is_product_owner = CheckWitness(owner)
    if not is_product_owner:
        print('Not the product or license owner!')
        return False
    return is_product_owner



