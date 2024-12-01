from intent.app import ui

def test_ui_features():
    features = dir(ui)
    for item in ['err', 'warn', 'print']:
        assert item in features
    