from decimal import Decimal

from webpy.manager import expose


@expose(name='Foo', url='/test')
def foo(a: int, b: Decimal, c: str, team: int) -> float:
    return 3
