"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock
from queue import Full

class SafeList:
    """
    Class that represents a Thread-safe List. This makes sure that no concurrent issue can arise.
    This implementation also allows a maxsize, which restricts insertions (it can also be
    disregarded through the use of "put_anyway").
    """
    def __init__(self, maxsize=0):
        """
        Constructor
        """
        self.mutex = Lock()
        self.list = []
        self.maxsize = maxsize

    def put(self, item):
        """
        Add an item to the list if the maxsize has not been reached.
        Otherwise, raise Full exception.
        """
        with self.mutex:
            if self.maxsize != 0 and self.maxsize == len(self.list):
                raise Full

            self.list.append(item)

    def put_anyway(self, item):
        """
        Add an item to the list, regardless of maxsize.
        """
        with self.mutex:
            self.list.append(item)

    def remove(self, item):
        """
        Try to remove an item from a list. If item is not found, return False. Else return True.
        """
        with self.mutex:
            if item not in self.list:
                return False

            self.list.remove(item)
            return True

class Cart:
    """
    Class that represents a Shopping Cart, that keeps track of the producers ID for
    each product.
    """

    def __init__(self):
        """
        Constructor
        """
        self.products = []

    def add_product(self, product, producer_id):
        """
        Adds a product, along with its producer ID.
        """
        self.products.append({"product": product, "producer_id": producer_id})

    def remove_product(self, product):
        """
        Removes a product and returns its producer ID, if found. If not found,
        return None.
        """
        for item in self.products:
            if item["product"] == product:
                self.products.remove(item)
                return item["producer_id"]

        return None

    def get_products(self):
        """
        Returns the list of products in the shopping cart.
        """
        return map(lambda item: item["product"], self.products)

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        self.producer_queues = {}
        self.producer_id_generator = 0
        self.producer_id_generator_lock = Lock()

        self.carts = {}
        self.cart_id_generator = 0
        self.cart_id_generator_lock = Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.producer_id_generator_lock:
            current_prod_id = self.producer_id_generator
            self.producer_queues[current_prod_id] = SafeList(maxsize=self.queue_size_per_producer)

            self.producer_id_generator += 1
            return current_prod_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        try:
            self.producer_queues[producer_id].put(product)
            return True
        except Full:
            return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        with self.cart_id_generator_lock:
            current_cart_id = self.cart_id_generator
            self.carts[current_cart_id] = Cart()

            self.cart_id_generator += 1
            return current_cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        producers_num = 0
        with self.producer_id_generator_lock:
            producers_num = self.producer_id_generator

        for producer_id in range(producers_num):
            # Try and remove the product from this producer's list.
            if self.producer_queues[producer_id].remove(product):
                self.carts[cart_id].add_product(product, producer_id)
                return True

        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        producer_id = self.carts[cart_id].remove_product(product)

        # Put back in producer's queue:
        self.producer_queues[producer_id].put_anyway(product)

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        return self.carts[cart_id].get_products()
