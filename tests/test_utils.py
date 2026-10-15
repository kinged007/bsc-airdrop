import utils


def test_load_config_missing_returns_none():
    assert utils.load_config(file="/tmp/__definitely_missing_12345.ini") is None


def test_load_config_reads_file(tmp_path):
    p = tmp_path / "test.ini"
    p.write_text("[Common]\nchain_id = 97\nnode_http_url = https://example.com\n")
    cfg = utils.load_config(file=str(p))
    assert cfg is not None
    assert cfg.get("Common", "chain_id") == "97"


def test_merge_dicts_overwrite():
    base = {"a": {"x": 1}}
    merged = utils.merge_dicts(dict(base), {"a": {"y": 2}})
    assert merged["a"]["x"] == 1
    assert merged["a"]["y"] == 2


def test_merge_dicts_no_overwrite():
    base = {"a": 1}
    merged = utils.merge_dicts(dict(base), {"a": 2}, overwrite=False)
    assert merged["a"] == 1


def test_clean_string():
    assert utils.cleanString("hello/world") == "hello_world"
    assert "_at_" in utils.cleanString("@test")


def test_replace_all():
    assert utils.replace_all("a-b-c", {"-": "_"}) == "a_b_c"


def test_format_time_returns_string():
    s = utils.FormatTime()
    assert isinstance(s, str)
    assert len(s) > 0
