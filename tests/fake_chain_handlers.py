from handlerchief.chain_handler import ChainHandler


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
