from pathlib import Path
import os
import sys
sys.path.append(os.fspath(Path(__file__).parent.parent.resolve()))

import unittest

from src.multi_handler import MultiHandler


class SumHandler(MultiHandler):
  def __init__(self, next=None):
    super().__init__(next=next)
    self.result = None

  def _can_handle(self, request) -> bool:
    return 'sum' in request['type']

  def _on_handle(self, request) -> bool:
    self.result = request['a'] + request['b']
    # this one will not stop execution if it can handle the request
    return False

  def _on_cannot_handle(self, request) -> bool:
    # this one will enable the next handler to
    # try and handle the request in case it cannot
    return False


class ProductHandler(MultiHandler):
  def __init__(self, next=None):
    super().__init__(next=next)
    self.result = None

  def _can_handle(self, request) -> bool:
    return 'product' in request['type']

  def _on_handle(self, request) -> bool:
    self.result = request['a'] * request['b']
    # this one will not stop execution if it can handle the request
    return False

  def _on_cannot_handle(self, request) -> bool:
    # this one will not enable the next handler to
    # try and handle the request in case it cannot
    return True


class DifferenceHandler(MultiHandler):
  def __init__(self, next=None):
    super().__init__(next=next)
    self.result = None

  def _can_handle(self, request) -> bool:
    return 'difference' in request['type']

  def _on_handle(self, request) -> bool:
    self.result = request['a'] - request['b']
    # this one will stop execution if it can handle the request
    return True

  def _on_cannot_handle(self, request) -> bool:
    # this one will enable the next handler to
    # try and handle the request in case it cannot
    return False


class RatioHandler(MultiHandler):
  def __init__(self, next=None):
    super().__init__(next=next)
    self.result = None

  def _can_handle(self, request) -> bool:
    return 'ratio' in request['type']

  def _on_handle(self, request) -> bool:
    self.result = request['a'] / request['b']
    # this one will stop execution if it can handle the request
    return True

  def _on_cannot_handle(self, request) -> bool:
    # this one will not enable the next handler to
    # try and handle the request in case it cannot
    return True


class TestMultiHandler(unittest.TestCase):
  def setUp(self) -> None:
    self.sum_handler = SumHandler()
    self.product_handler = ProductHandler()
    self.difference_handler = DifferenceHandler()
    self.ratio_handler = RatioHandler()
    
    self.sum_handler.set_next(
      self.product_handler
    ).set_next(
      self.difference_handler
    ).set_next(
      self.ratio_handler
    )

    self.chain = self.sum_handler

  def test_concats_in_proper_order(self):
    self.assertEqual(self.chain, self.sum_handler)
    self.assertEqual(self.chain.next, self.product_handler)
    self.assertEqual(self.chain.next.next, self.difference_handler)
    self.assertEqual(self.chain.next.next.next, self.ratio_handler)

  def test_continues_execution_when_it_can_handle_and_it_does_not_exit(self):
    request = {
      'type': ['product', 'difference'],
      'a': 1,
      'b': 2
    }

    self.chain.handle(request)

    expected_product = 2
    observed_product = self.product_handler.result
    self.assertEqual(expected_product, observed_product)

    expected_difference = -1
    observed_difference = self.difference_handler.result
    self.assertEqual(expected_difference, observed_difference)

  def test_continues_execution_when_it_cannot_handle_and_it_does_not_exit(
    self
  ):
    request = {
      'type': ['product'],
      'a': 1,
      'b': 2
    }

    self.chain.handle(request)

    expected_product = 2
    observed_product = self.product_handler.result
    self.assertEqual(expected_product, observed_product)

  def test_stops_execution_when_it_can_handle_and_it_exits(self):
    request = {
      'type': ['product', 'difference', 'ratio'],
      'a': 1,
      'b': 2
    }

    self.chain.handle(request)

    expected_difference = -1
    observed_difference = self.difference_handler.result
    self.assertEqual(expected_difference, observed_difference)

    expected_ratio = None
    observed_ratio = self.ratio_handler.result
    self.assertEqual(expected_ratio, observed_ratio)

  def test_stops_execution_when_it_cannot_handle_and_it_exits(self):
    request = {
      'type': ['difference'],
      'a': 1,
      'b': 2
    }

    self.chain.handle(request)

    expected_difference = None
    observed_difference = self.difference_handler.result
    self.assertEqual(expected_difference, observed_difference)


if __name__ == '__main__':
  unittest.main()
