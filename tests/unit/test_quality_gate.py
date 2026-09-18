from src.app.quality import calculate_gate

def test_quality_gate_pass():
    gate = calculate_gate([0.91, 0.94, 0.89], .85, .60, .20)
    assert gate.passed
    assert gate.minimum == .89

def test_quality_gate_fail_on_minimum():
    gate = calculate_gate([0.95, 0.95, 0.59], .85, .60, .20)
    assert not gate.passed
