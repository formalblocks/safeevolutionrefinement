import pytest
from gen.read import readl_yaml_str
from gen.model import *

def test_read_yaml_two():
    instances = readl_yaml_str(
    """
    source:
        - name: a
        type: Uint
        values:
        - sim: 1
            evaluation: 5
        - sim: 2
            evaluation: 10
    target:
        - name: a_
        type: Uint
        values:
        - sim: 1
            evaluation: 10
        - sim: 2
            evaluation: 20  
    """
    )
    assert len(instances) == 4
    first = instances[0]
    fourth = instances[3]
    assert first.version == ContractVersion.Source
    assert first.simulation == Simulation(1)
    assert len(first.variables) == 1 and len(first.assignments) == 1 and first.assignments[0].value == 5
    assert fourth.version == ContractVersion.Target
    assert len(fourth.variables) == 1 and len(fourth.assignments) == 1 and fourth.assignments[0].value == 20


def test_read_yaml_two():
    instances = readl_yaml_str(
    """
    source:
    - name: a
      type: Uint
      values:
      - sim: 1
        evaluation: 5
      - sim: 2
        evaluation: 5
    - name: b
      type: Uint
      values:
      - sim: 1
        evaluation: 10
      - sim: 2
        evaluation: 5
    target:
    - name: a_
      type: Uint
      values:
      - sim: 1
        evaluation: 10
      - sim: 2
        evaluation: 5
    - name: b
      type: Uint
      values:
      - sim: 1
        evaluation: 20
      - sim: 2
        evaluation: 25
    """
    )
    assert len(instances) == 4
    first = instances[0]
    fourth = instances[3]
    assert first.version == ContractVersion.Source
    assert first.simulation == Simulation(1)
    assert len(first.variables) == 2 and len(first.assignments) == 2 and first.assignments[0].value == 5
    assert len(fourth.variables) == 2 and len(fourth.assignments) == 2 and fourth.assignments[1].variable.name == 'b' and fourth.assignments[1].value == 25

def test_read_mapping():
    instances = readl_yaml_str(
    """
    source:
        - name: a
          type: MappingType
          keyType: Address
          valueType: Uint
          values:
            - sim: 1
              evaluation:
                Addr123: 1
                Addr345 (signature): 5
            - sim: 2
              evaluation:
                0: 5
                1: 10
    target:
        - name: a_
          type: MappingType
          keyType: Address
          valueType: Uint
          values:
            - sim: 1
              evaluation:
                0: 2
                1: 6
            - sim: 2
              evaluation:
                0: 6
                1: 11  
    """
    )
    assert len(instances) == 4
    first = instances[0]
    fourth = instances[3]
    assert first.version == ContractVersion.Source
    assert first.simulation == Simulation(1)
    assert len(first.variables) == 1 and len(first.assignments) == 1
    assert fourth.version == ContractVersion.Target
    assert len(fourth.variables) == 1 and len(fourth.assignments) == 1
    assert fourth.assignments[0].value == {0: 6, 1: 11}

def test_read_mapping_no_value_type():
    with pytest.raises(AssertionError, match='The valueType must be declared for MappingType'):
      readl_yaml_str(
      """
      source:
          - name: a
            type: MappingType
            keyType: Address
            values:
              - sim: 1
                evaluation:
                  Addr123: 1
                  Addr345 (signature): 5
              - sim: 2
                evaluation:
                  0: 5
                  1: 10
      target:
          - name: a_
            type: MappingType
            valueType: Uint
            values:
              - sim: 1
                evaluation:
                  0: 2
                  1: 6
              - sim: 2
                evaluation:
                  0: 6
                  1: 11  
      """
      )

def test_read_mapping_struct_value():
      instances = readl_yaml_str(
      """
      source:
          - name: a
            type: MappingType
            keyType: Uint
            valueType: Struct
            valueAttrs: [a, b]
            values:
              - sim: 1
                evaluation:
                  0: {a: 1, b: 2}
                  1: {a: 3, b: 4}
              - sim: 2
                evaluation:
                  0: {a: 1, b: 2}
                  1: {a: 3, b: 4}
      target:
          - name: a_
            type: MappingType
            keyType: Uint
            valueType: Uint
            valueAttrs: [a, b] 
            values:
              - sim: 1
                evaluation:
                  0: {a: 1, b: 2}
                  1: {a: 3, b: 4}
              - sim: 2
                evaluation:
                  0: {a: 1, b: 2}
                  1: {a: 3, b: 4} 
      """
      )


def test_read_struct():
    instances = readl_yaml_str(
    """
    source:
        - name: x
          type: Struct
          attrs: [a, b]
          values:
            - sim: 1
              evaluation:
                a: 1
                b: 2
            - sim: 2
              evaluation:
                a: 3
                b: 4
    target:
        - name: a_
          type: Uint
          values:
            - sim: 1
              evaluation: 1
            - sim: 2
              evaluation: 3
        - name: b_
          type: Uint
          values:
            - sim: 1
              evaluation: 2
            - sim: 2
              evaluation: 4 
    """
    )
    assert len(instances) == 4
    first = instances[0]
    fourth = instances[3]
    assert first.version == ContractVersion.Source
    assert first.simulation == Simulation(1)
    assert len(first.variables) == 1 and len(first.assignments) == 1
    assert isinstance(list(first.variables)[0], StructVariable)
    assert list(first.variables)[0].attrs == ('a', 'b')
    assert first.assignments[0].value['b'] == 2
    assert fourth.version == ContractVersion.Target
    assert len(fourth.variables) == 2 and len(fourth.assignments) == 2
    assert fourth.assignments[0].value == 3

def test_read_struct_undeclared_attr():
    
    with pytest.raises(AssertionError, match='b must be declared in attrs'):
      readl_yaml_str(
      """
      source:
          - name: x
            type: Struct
            attrs: [a]
            values:
              - sim: 1
                evaluation:
                  a: 1
                  b: 2
              - sim: 2
                evaluation:
                  a: 3
                  b: 4
      target:
          - name: x
            type: Struct
            attrs: [a]
            values:
              - sim: 1
                evaluation:
                  a: 1
                  b: 2
              - sim: 2
                evaluation:
                  a: 3
      """
      )