from pathlib import Path
import os
import sys
sys.path.append(os.fspath(Path(__file__).parent.parent.resolve()))

from typing import Tuple
import unittest

from src.i_middleware_handler import IMiddlewareHandler


class SumHandler(IMiddlewareHandler):
  def _can_handle(self, request, response) -> bool:
    return 'sum' in request['type']

  def _on_handle(self, request, response) -> Tuple[any, any]:
    response['execution_order'].append('sum')
    response['result'] = response['result'] + request['a']
    return (request, response)

  def _on_cannot_handle(self, request, response):
    # this one continues execution with the next handler
    # if it cannot handle the request
    return self._next.handle(request, response)

class ProductHandler(IMiddlewareHandler):
  def _can_handle(self, request, response) -> bool:
    return 'product' in request['type']

  def _on_handle(self, request, response) -> Tuple[any, any]:
    response['execution_order'].append('product')
    response['result'] = response['result'] * request['a']
    return (request, response)

  def _on_cannot_handle(self, request, response):
    # this one continues execution with the next handler
    # if it cannot handle the request
    return self._next.handle(request, response)

class DifferenceHandler(IMiddlewareHandler):
  def _can_handle(self, request, response) -> bool:
    return 'difference' in request['type']

  def _on_handle(self, request, response) -> Tuple[any, any]:
    response['execution_order'].append('difference')
    response['result'] = response['result'] - request['a']
    # this one modifies request too
    request['extra'] = 'extra'
    return (request, response)

  def _on_cannot_handle(self, request, response):
    # this one stops execution
    # if it cannot handle the request
    return (request, response)

class RatioHandler(IMiddlewareHandler):
  def _can_handle(self, request, response) -> bool:
    return 'ratio' in request['type']

  def _on_handle(self, request, response) -> Tuple[any, any]:
    response['execution_order'].append('ratio')
    response['result'] = response['result'] / request['a']
    return (request, response)

  def _on_cannot_handle(self, request, response):
    # this one stops execution
    # if it cannot handle the request
    return (request, response)

class TestMiddlewareHandler(unittest.TestCase):
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

  def test_executes_all_properly_if_able_to(self):
    request = {
      'type': ['sum', 'product', 'difference', 'ratio'],
      'a': 2
    }
    response = {
      'result': 1,
      'execution_order': []
    }

    self.chain.handle(request, response)

    expected_result = 2
    observed_result = response['result']
    self.assertEqual(expected_result, observed_result)

    expected_execution_order = ['sum', 'product', 'difference', 'ratio']
    observed_execution_order = response['execution_order']
    self.assertListEqual(expected_execution_order, observed_execution_order)

  def test_can_modify_request(self):
    request = {
      'type': ['sum', 'product', 'difference', 'ratio'],
      'a': 2
    }
    response = {
      'result': 1,
      'execution_order': []
    }

    self.chain.handle(request, response)

    self.assertTrue('extra' in request.keys())

    expected = 'extra'
    observed = request['extra']
    self.assertEqual(expected, observed)

  def test_stops_execution_when_it_cannot_handle_and_exits(self):
    request = {
      'type': ['sum', 'product', 'ratio'],
      'a': 2
    }
    response = {
      'result': 1,
      'execution_order': []
    }

    self.chain.handle(request, response)

    expected_result = 6
    observed_result = response['result']
    self.assertEqual(expected_result, observed_result)

    expected_execution_order = ['sum', 'product']
    observed_execution_order = response['execution_order']
    self.assertListEqual(expected_execution_order, observed_execution_order)

  def test_skips_handler_when_it_cannot_handle_and_it_does_not_exit(self):
    request = {
      'type': ['sum', 'difference', 'ratio'],
      'a': 2
    }
    response = {
      'result': 1,
      'execution_order': []
    }

    self.chain.handle(request, response)

    expected_result = 0.5
    observed_result = response['result']
    self.assertEqual(expected_result, observed_result)

    expected_execution_order = ['sum', 'difference', 'ratio']
    observed_execution_order = response['execution_order']
    self.assertListEqual(expected_execution_order, observed_execution_order)


if __name__ == '__main__':
  unittest.main()
