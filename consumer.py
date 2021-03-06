"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.name = kwargs["name"]
    def run(self):
        for cart in self.carts:
            # Get a new shopping cart ID.
            cart_id = self.marketplace.new_cart()

            for operation in cart:
                # For every item, either add one to the cart or remove one.
                for _ in range(operation["quantity"]):
                    if operation["type"] == "add":
                        while not self.marketplace.add_to_cart(cart_id, operation["product"]):
                            sleep(self.retry_wait_time) # wait until product is available
                    elif operation["type"] == "remove":
                        self.marketplace.remove_from_cart(cart_id, operation["product"])

            products = self.marketplace.place_order(cart_id)

            # Display products acquired:
            for product in products:
                print("{0} bought {1}".format(self.name, product))
