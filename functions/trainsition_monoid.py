from models import FiniteAutomaton
import functions.registry as registry
from monoid import monoid

@registry.register(registry.FunctionType.PREDICATE)
def transitionmonoid(fa: FiniteAutomaton) -> None:
    if not fa.is_deterministic:
      raise Exception('DFA is not detemenistic')
        return
        
