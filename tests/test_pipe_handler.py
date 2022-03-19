from pathlib import Path
import os
import sys
path = os.fspath((Path(__file__).parent.parent / 'src').resolve())
if path not in sys.path:
    sys.path.append(path)

import unittest

from handlerchief.pipe_handler import PipeHandler


class SumHandler(PipeHandler):
  def _can_handle(self, request) -> bool:
    return 'sum' in request['type']

  def _on_handle(self, request):
    request['execution_order'].append('sum')
    request['result'] = request['result'] + request['a']
    return request

  def _on_cannot_handle(self, request):
    # this one continues execution with the next handler
    # if it cannot handle the request
    return self._next.handle(request)

class ProductHandler(PipeHandler):
  def _can_handle(self, request) -> bool:
    return 'product' in request['type']

  def _on_handle(self, request):
    request['execution_order'].append('product')
    request['result'] = request['result'] * request['a']
    return request

  def _on_cannot_handle(self, request):
    # this one continues execution with the next handler
    # if it cannot handle the request
    return self._next.handle(request)

class DifferenceHandler(PipeHandler):
  def _can_handle(self, request) -> bool:
    return 'difference' in request['type']

  def _on_handle(self, request):
    request['execution_order'].append('difference')
    request['result'] = request['result'] - request['a']
    return request

  def _on_cannot_handle(self, request):
    # this one stops execution
    # if it cannot handle the request
    return request

class RatioHandler(PipeHandler):
  def _can_handle(self, request) -> bool:
    return 'ratio' in request['type']

  def _on_handle(self, request):
    request['execution_order'].append('ratio')
    request['result'] = request['result'] / request['a']
    return request

  def _on_cannot_handle(self, request):
    # this one stops execution
    # if it cannot handle the request
    return request

class TestPipeHandler(unittest.TestCase):
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
      'a': 2,
      'result': 1,
      'execution_order': []
    }

    self.chain.handle(request)

    expected_result = -1
    observed_result = request['result']
    self.assertEqual(expected_result, observed_result)

    expected_execution_order = ['ratio', 'difference', 'product', 'sum']
    observed_execution_order = request['execution_order']
    self.assertListEqual(expected_execution_order, observed_execution_order)

  def test_stops_execution_when_it_cannot_handle_and_exits(self):
    request = {
      'type': ['sum', 'product', 'ratio'],
      'a': 2,
      'result': 1,
      'execution_order': []
    }

    self.chain.handle(request)

    expected_result = 4
    observed_result = request['result']
    self.assertEqual(expected_result, observed_result)

    expected_execution_order = ['product', 'sum']
    observed_execution_order = request['execution_order']
    self.assertListEqual(expected_execution_order, observed_execution_order)

  def test_skips_handler_when_it_cannot_handle_and_it_does_not_exit(self):
    request = {
      'type': ['sum', 'difference', 'ratio'],
      'a': 2,
      'result': 1,
      'execution_order': []
    }

    self.chain.handle(request)

    expected_result = 0.5
    observed_result = request['result']
    self.assertEqual(expected_result, observed_result)

    expected_execution_order = ['ratio', 'difference', 'sum']
    observed_execution_order = request['execution_order']
    self.assertListEqual(expected_execution_order, observed_execution_order)

if __name__ == '__main__':
  unittest.main()
