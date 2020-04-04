from abc import ABC, abstractmethod


class FilterDecorator(ABC):
    def __init__(self, *component_types):
        self.component_types = component_types

    def __call__(self, system_class):
        system_class.__clauses__ = self._clauses
        return system_class

    @abstractmethod
    def _clauses(self, entity):
        pass


class requires(FilterDecorator):
    """Decorator object adds required components clauses to System class."""

    def _clauses(self, entity):
        return entity.has_components(*self.component_types)


class excludes(FilterDecorator):
    """Decorator object add component except excluded clauses to System class."""

    def _clauses(self, entity):
        return not any(
            ct in entity._components for ct in self.component_types
        )


class Component:
    pass


class System(ABC):
    __clauses__ = None

    def __init__(self):
        self.world = None
        self.priority = None

    @property
    def required_entities(self):
        assert self.world, 'No world for this System'
        return self.world.filtered_entities(self.__clauses__)

    @abstractmethod
    def update(self, *args, **kwargs):
        pass


class Entity:
    def __init__(self, id, world, *components):
        self._id = id
        assert isinstance(world, World), 'world is not instance of World class'
        self.world = world
        self._components = {type(c): c for c in components}

    def __repr__(self):
        return f'Entity({", ".join(str(c) for c in self.components)})'

    def __eq__(self, other):
        self._id = other.id

    def __hash__(self):
        return hash(self._id)

    @property
    def components(self):
        return tuple(self._components.values())

    def add_component(self, component):
        self._components[type(component)] = component

    def remove_component(self, component_type):
        self._components.pop(component_type)

    def get_component(self, component_type):
        return self._components[component_type]

    def has_component(self, component_type):
        return component_type in self._components

    def has_components(self, *component_types):
        return all(ct in self._components for ct in component_types)


class World:
    def __init__(self):
        self._systems = []
        self._next_entity_id = 0
        self._entities = set()
        self._dead_entities = set()

    def add_system(self, system, priority=0):
        assert issubclass(system.__class__, System),\
            'system class is not subclass of System'
        system.world = self
        system.priority = priority
        self._systems.append(system)
        self._systems.sort(key=lambda sys: sys.priority, reverse=True)

    def remove_system(self, system_type):
        for system in self._systems:
            if type(system) == system_type:
                system.world = None
                system.priority = None
                self._systems.remove(system)

    def get_system(self, system_type):
        for system in self._systems:
            if type(system) == system_type:
                return system

    def create_entity(self, *components):
        self._next_entity_id += 1
        entity = Entity(self._next_entity_id, self, *components)
        self._entities.add(entity)
        return entity

    def delete_entity(self, entity, immediate=False):
        if immediate:
            self._entities.remove(entity)
        else:
            self._dead_entities.add(entity)

    def filtered_entities(self, clauses):
        return tuple(e for e in self._entities if clauses(e))

    def update(self, *args, **kwargs):
        self._delete_dead_entities()
        for system in self._systems:
            system.update(*args, **kwargs)

    def clear(self):
        self._next_entity_id = 0
        self._entities.clear()
        self._dead_entities.clear()

    def _delete_dead_entities(self):
        for entity in self._dead_entities:
            self._entities.remove(entity)
        self._dead_entities.clear()
