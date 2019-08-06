from decimal import Decimal

from webpy.manager import expose


@expose(name='Foo', url='/test')
def foo(a: int, b: Decimal, c: str, team: int) -> Decimal:
    return Decimal(3)


@expose(name='Add two numbers', url='/add')
def add(a: int, b: int) -> int:
    return a + b
