from gen.alloy import AlloyInferEngine
from gen.model import InferEngine, Solution
from gen.read import readl_yaml_str

def test_simple_alloy():
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
        - name: _a
          type: Uint
          values:
            - sim: 1
              evaluation: 10
            - sim: 2
              evaluation: 20
    """
    )
    inference_engine: InferEngine = AlloyInferEngine
    instance: Solution = inference_engine.infer(instances)
    assert len(instance.inferred_relations) == 1
    assert str(instance.inferred_relations[0]) in ['_a == a * 2', '_a == a + a', '_a == 2 * a',]

def test_variables_alloy():
    instances = readl_yaml_str(
    """
    source:
        - name: a
          type: Uint
          values:
            - sim: 1
              evaluation: 2
            - sim: 2
              evaluation: 3
        - name: c
          type: Uint
          values:
            - sim: 1
              evaluation: 2
            - sim: 2
              evaluation: 4
    target:
        - name: _a
          type: Uint
          values:
            - sim: 1
              evaluation: 4
            - sim: 2
              evaluation: 12
    """
    )
    inference_engine: InferEngine = AlloyInferEngine
    instance: Solution = inference_engine.infer(instances)
    assert len(instance.inferred_relations) == 1
    assert str(instance.inferred_relations[0]) in ['_a == a * c', '_a == c * a']

## criar teste com relação de duas variáveis diferentes
def test_equals_alloy():
    instances = readl_yaml_str(
    """
    source:
        - name: a
          type: Uint
          values:
            - sim: 1
              evaluation: 10
            - sim: 2
              evaluation: 10
    target:
        - name: _a
          type: Uint
          values:
            - sim: 1
              evaluation: 10
            - sim: 2
              evaluation: 10
    """
    )
    inference_engine: InferEngine = AlloyInferEngine
    instance: Solution = inference_engine.infer(instances)
    assert len(instance.inferred_relations) == 1
    assert str(instance.inferred_relations[0]) == '_a == a'

def test_two_variables_alloy():
    instances = readl_yaml_str(
    """
    source:
        - name: a
          type: Uint
          values:
            - sim: 1
              evaluation: 10
            - sim: 2
              evaluation: 10
        - name: b
          type: Uint
          values:
            - sim: 1
              evaluation: 20
            - sim: 2
              evaluation: 20
    target:
        - name: _a
          type: Uint
          values:
            - sim: 1
              evaluation: 10
            - sim: 2
              evaluation: 10
        - name: b
          type: Uint
          values:
            - sim: 1
              evaluation: 20
            - sim: 2
              evaluation: 20
    """
    )
    inference_engine: InferEngine = AlloyInferEngine
    instance: Solution = inference_engine.infer(instances)
    assert len(instance.inferred_relations) == 2
    assert set(str(rel) for rel in instance.inferred_relations) == set(['_a == a', 'b == b'])


def test_simple_mapping_alloy():
    instances = readl_yaml_str(
    """
    source:
        - name: a
          type: MappingType
          keyType: Uint
          valueType: Uint
          values:
            - sim: 1
              evaluation:
                0: 1
            - sim: 2
              evaluation:
                0: 5
    target:
        - name: a_
          type: MappingType
          keyType: Uint
          valueType: Uint
          values:
            - sim: 1
              evaluation:
                0: 2
            - sim: 2
              evaluation:
                0: 6
    """
    )
    inference_engine: InferEngine = AlloyInferEngine
    instance: Solution = inference_engine.infer(instances)
    assert len(instance.inferred_relations) == 1
    assert str(instance.inferred_relations[0]) in ['forall (uint i) a_[i] == 1 + a[i]', 'forall (uint i) a_[i] == a[i] + 1']

def test_two_keys_mapping_alloy():
    instances = readl_yaml_str(
    """
    source:
        - name: a
          type: MappingType
          keyType: Uint
          valueType: Uint
          values:
            - sim: 1
              evaluation:
                0: 5
                1: 6
            - sim: 2
              evaluation:
                0: 5
                1: 6
    target:
        - name: a_
          type: MappingType
          keyType: Uint
          valueType: Uint
          values:
            - sim: 1
              evaluation:
                0: 5
                1: 6
            - sim: 2
              evaluation:
                0: 5
                1: 6
    """
    )
    inference_engine: InferEngine = AlloyInferEngine
    instance: Solution = inference_engine.infer(instances)
    assert len(instance.inferred_relations) == 1
    assert str(instance.inferred_relations[0]) in ['__verifier_eq(a_, a)','__verifier_eq(a, a_)']


def test_mapping_struct_alloy():
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
      """
    )
    inference_engine: InferEngine = AlloyInferEngine
    instance: Solution = inference_engine.infer(instances)
    assert len(instance.inferred_relations) == 2
    assert str(instance.inferred_relations[0]) in ['forall (uint i) a_[i].b == a[i].b','forall (uint i) a_[i].a == a[i].a']

def test_auction_alloy():
    instances = readl_yaml_str(
    """
    target:
        - name: auctionEnd
          type: Uint
          values:
            - sim: 1
              evaluation: 5
            - sim: 2
              evaluation: 6
    source:
        - name: auctionStart
          type: Uint
          values:
            - sim: 1
              evaluation: 1
            - sim: 2
              evaluation: 3
        - name: biddingTime
          type: Uint
          values:
            - sim: 1
              evaluation: 4
            - sim: 2
              evaluation: 3
    """
    )
    inference_engine: InferEngine = AlloyInferEngine
    instance: Solution = inference_engine.infer(instances)
    assert len(instance.inferred_relations) == 1
    assert str(instance.inferred_relations[0]) in ['auctionEnd == auctionStart + biddingTime', 'auctionEnd == biddingTime + auctionStart']


## criar teste com relação de duas variáveis diferentes
def test_aplusb_cminusd():
    instances = readl_yaml_str(
    """
    source:
        - name: a
          type: Uint
          values:
            - sim: 1
              evaluation: 10
        - name: b
          type: Uint
          values:
            - sim: 1
              evaluation: -5
    target:
        - name: c
          type: Uint
          values:
            - sim: 1
              evaluation: 10

        - name: d
          type: Uint
          values:
            - sim: 1
              evaluation: 5
    """
    )
    inference_engine: InferEngine = AlloyInferEngine
    instance: Solution = inference_engine.infer(instances)
    assert len(instance.inferred_relations) == 2
    assert set(str(rel) for rel in instance.inferred_relations) in [set(['d == b * -1', 'c == a']), set(['d == a + b', 'c == a']),
                                                                    set(['c == a', 'd == b + a'])] # Possible but not correct after verification


def test_simple_struct_alloy():
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
    inference_engine: InferEngine = AlloyInferEngine
    instance: Solution = inference_engine.infer(instances)
    assert len(instance.inferred_relations) == 2
    assert set(str(rel) for rel in instance.inferred_relations) in [set(['x.a == a_','x.b == b_']), set(['a_ == x.a','b_ == x.b'])]

def test_struct_to_mappings():
    instances = readl_yaml_str(
    """
    source:
        - name: x
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
                0: {a: 2, b: 3}
                1: {a: 4, b: 5}
    target:
        - name: a
          type: MappingType
          keyType: Uint
          valueType: Uint
          values:
            - sim: 1
              evaluation:
                0: 1
                1: 3
            - sim: 2
              evaluation:
                0: 2
                1: 4
        - name: b
          type: MappingType
          keyType: Uint
          valueType: Uint
          values:
            - sim: 1
              evaluation:
                0: 2
                1: 4
            - sim: 2
              evaluation:
                0: 3
                1: 5
    """
    )
    inference_engine: InferEngine = AlloyInferEngine
    instance: Solution = inference_engine.infer(instances)
    assert len(instance.inferred_relations) == 2
    assert set(str(rel) for rel in instance.inferred_relations) == set(['forall (uint i) a[i] == x[i].a','forall (uint i) b[i] == x[i].b'])