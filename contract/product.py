from boa.blockchain.vm.Neo.Storage import GetContext, Get
from contract.serialize import deserialize_bytearray


class Product():
    owner = "a"
    id = "a"
    desc = "a"
    mln = 1
    trans = True
    pe = 1
    le = 1
    cln = 1


def init_product(product_id) -> Product:
    """
    class __init__ method is currently not supported.
    :return: Product instance
    """
    serialized_product_data = Get(GetContext, product_id)
    product_list = deserialize_bytearray(serialized_product_data)

    product = Product()

    product.owner = product_list[0]
    product.id = product_list[1]
    product.desc = product_list[2]
    product.mln = product_list[3]
    product.trans = product_list[4]
    product.pe = product_list[5]
    product.le = product_list[6]
    product.cln = product_list[7]

    return product


def get_all_product(product: Product):
    all_data = [product.owner, product.id, product.desc,
                product.mln, product.trans, product.pe,
                product.le, product.cln]

    return all_data
