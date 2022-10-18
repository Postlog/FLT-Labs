from models import NFA, Regex, Int
import functions.registry as registry


@registry.register(registry.FunctionType.EXTRA)
def test(v: NFA | Regex, regex: Regex, i: Int) -> None:
    raise NotImplementedError('TestFunction not implemented')
