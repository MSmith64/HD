import sys
sys.path.insert(0, '/mnt/data/hd_app')
from hd_engine import full_address, compute_chart, CHANNELS

def test_gate_wheel_anchor():
    a=full_address(302.0)
    assert a == {'gate':41,'line':1,'color':1,'tone':1,'base':1}

def test_chart_shape():
    c=compute_chart(name='Test',year=1990,month=7,day=15,hour=14,minute=30,tz_name='Europe/London')
    assert c['type'] in {'Manifestor','Generator','Manifesting Generator','Projector','Reflector'}
    assert len(c['personality']) == 13
    assert len(c['design']) == 13
    assert all(1 <= x['gate'] <= 64 for x in c['personality'].values())
    assert all(1 <= x['line'] <= 6 for x in c['personality'].values())
    assert all(1 <= x['color'] <= 6 for x in c['personality'].values())
    assert all(1 <= x['tone'] <= 6 for x in c['personality'].values())
    assert all(1 <= x['base'] <= 5 for x in c['personality'].values())
    assert all(ch['name'] for ch in c['channels'])
    assert len(CHANNELS) == 36
