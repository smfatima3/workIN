import pytest
from mrs.foundation_policy import parse_final,action_prompt

def test_final_parser_preserves_final_answer_and_rejects_truncation():
    assert parse_final('<think>private reasoning</think>\n{"action":"detour"}',True)=={'action':'detour'}
    assert parse_final('```json\n{"belief":"unknown"}\n```')=={'belief':'unknown'}
    with pytest.raises(ValueError):parse_final('<think>unfinished',True)
    with pytest.raises(ValueError):parse_final('{"action":')

def test_action_interface_does_not_infer_unknown_permission():
    text=action_prompt('exclusion','unknown',[])
    assert 'ENTERS the zone' in text and 'must not enter' in text
    assert 'No permission is supplied' in text
    assert 'true' not in text.lower() and 'poison' not in text.lower()
