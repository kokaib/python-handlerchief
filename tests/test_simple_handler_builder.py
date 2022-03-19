from pathlib import Path
import os
import sys
from unittest.mock import Mock
path = os.fspath((Path(__file__).parent.parent / 'src').resolve())
if path not in sys.path:
    sys.path.append(path)

import unittest

from handlerchief.simple_handler_builder import SimpleHandlerBuilder
from .fake_chain_handlers import SumHandler, ProductHandler, DifferenceHandler


class TestSimpleHandlerBuilder(unittest.TestCase):
  def test_can_seed_handlers(self):
    expected = [SumHandler(), ProductHandler(), DifferenceHandler()]
    under_test = SimpleHandlerBuilder(expected)
    actual = under_test._handlers

    self.assertListEqual(expected, actual)

  def test_can_add_handler(self):
    under_test = SimpleHandlerBuilder()
    expected = ['a', ProductHandler(), DifferenceHandler()]
    for handler in expected:
      under_test.add_next(handler)
    actual = under_test._handlers

    self.assertListEqual(expected, actual)

  def test_can_daisy_chain(self):
    under_test = SimpleHandlerBuilder()
    expected = [SumHandler(), ProductHandler(), DifferenceHandler()]
    self.assertEqual(3, len(expected))

    result = under_test.add_next(
      expected[0]
    ).add_next(
      expected[1]
    ).add_next(
      expected[2]
    )

    self.assertEqual(under_test, result)

    actual = under_test._handlers

    self.assertListEqual(expected, actual)


  def test_fails_if_too_few_handlers_were_added(self):
    under_test = SimpleHandlerBuilder()
    with self.assertRaises(ValueError) as context:
      under_test.build()

    self.assertEqual(
      'Too few handlers added to the builder.', str(context.exception)
    )

  def test_can_build(self):
    handlers = [Mock(), Mock(), Mock()]
    under_test = SimpleHandlerBuilder(handlers)
    
    result = under_test.build()

    self.assertEqual(handlers[0], result)

    for i in range(len(handlers) - 1):
      handlers[i].set_next.assert_called_once_with(handlers[i + 1])

    handlers[-1].set_next.assert_not_called()


if __name__ == '__main__':
  unittest.main()
