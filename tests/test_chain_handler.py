from pathlib import Path
import os
import sys
path = os.fspath((Path(__file__).parent.parent / 'src').resolve())
if path not in sys.path:
    sys.path.append(path)

import unittest

from .fake_chain_handlers import (
  SumHandler, ProductHandler, DifferenceHandler, RatioHandler
)


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
