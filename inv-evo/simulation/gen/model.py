import abc
from dataclasses import dataclass, field
from typing import List, Literal, Set
from enum import Enum

@dataclass(frozen=True)
class Type(Enum):
    Uint = 1
    MappingType = 2
    Struct = 3
    Address = 4

class ContractVersion(Enum):
    Source = 1
    Target = 2

    @staticmethod
    def from_str(version: Literal['source', 'target']):
        if version == 'source':
            return ContractVersion.Source
        elif version == 'target':
            return ContractVersion.Target
        else:
            raise ValueError('wrong version str')

@dataclass(frozen=True)
class Variable:
    name: str
    type: Type
    version: 'ContractVersion'

@dataclass(frozen=True)
class MappingVariable(Variable):
    keyType: Type
    valueType: Type
    valueAttrs: tuple[str] = field(default=(None,), init=True)
    type: Type = field(default=Type.MappingType, init=False)

@dataclass(frozen=True)
class StructVariable(Variable):
    attrs: tuple[str]
    type: Type = field(default=Type.Struct, init=False)


@dataclass(frozen=True)
class Assignment:
    variable: Variable
    simulation: 'Simulation'
    value: object

@dataclass(frozen=True)
class Contract:
    name: str

@dataclass(frozen=True)
class Simulation:
    id: int

@dataclass(frozen=True)
class ContractInstance:

    simulation: Simulation
    variables: List[Variable]
    assignments: List[Assignment]
    version: ContractVersion
    
    def __post_init__(self):
        # assert len(self.variables) == len(self.assignments)
        # assert set([assignment.variable for assignment in self.assignments]) == set(self.variables)
        for var in self.variables:
            assert var.version == self.version 
        for assignment in self.assignments:
            assert self.simulation == assignment.simulation

class InferEngine(abc.ABC):

    @abc.abstractstaticmethod
    def infer(instances) -> 'Solution':
        pass

class Relation:
    pass

class Solution(abc.ABC):
    
    @abc.abstractproperty
    def inferred_relations(self) -> list[Relation]:
        pass
