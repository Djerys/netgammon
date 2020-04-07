from dataclasses import dataclass
from code.base import system


@dataclass
class ComponentA(system.Component):
    a: int = 1


@dataclass
class ComponentB(system.Component):
    b: int = 2


@dataclass
class ComponentC(system.Component):
    c: int = 3


@system.requires(ComponentA, ComponentB)
class SomeSystem(system.System):
    def update(self):
        for entity in self.required_entities:
            component_a = entity.get_component(ComponentA)
            component_a.a += 1
            component_b = entity.get_component(ComponentB)
            component_b.b += 1


world = system.World()
e1 = world.create_entity(ComponentA(), ComponentB())
e2 = world.create_entity(ComponentA(), ComponentC())
e3 = world.create_entity(ComponentB(), ComponentC())
e4 = world.create_entity(ComponentC())
some_system = SomeSystem()
world.add_system(some_system)

while True:
    world.update()
