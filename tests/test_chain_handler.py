from pathlib import Path
import os
import sys
sys.path.append(os.fspath(Path(__file__).parent.parent.resolve()))

import unittest

from src.chain_handler import ChainHandler


class SumHandler(ChainHandler):
  def _can_handle(self, request) -> bool:
    return 'sum' in request['type']

  def _on_handle(self, request):
    return request['a'] + request['b']


class ProductHandler(ChainHandler):
  def _can_handle(self, request) -> bool:
    return 'product' in request['type']

  def _on_handle(self, request):
    return request['a'] * request['b']


class DifferenceHandler(ChainHandler):
  def _can_handle(self, request) -> bool:
    return 'difference' in request['type']

  def _on_handle(self, request):
    return request['a'] - request['b']


class RatioHandler(ChainHandler):
  def _can_handle(self, request) -> bool:
    return 'ratio' in request['type']

  def _on_handle(self, request):
    return request['a'] / request['b']


class TestChainHandler(unittest.TestCase):
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

  def test_executes_only_if_able_to(self):
    request = {
      'type': ['difference'],
      'a': 1,
      'b': 2
    }

    expected = -1
    observed = self.chain.handle(request)
    self.assertEqual(expected, observed)

  def test_executes_the_first_which_is_able_to(self):
    request = {
      'type': ['difference', 'product'],
      'a': 1,
      'b': 2
    }

    expected = 2
    observed = self.chain.handle(request)
    self.assertEqual(expected, observed)


if __name__ == '__main__':
  unittest.main()
