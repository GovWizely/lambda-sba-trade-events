import vcr

from service import get_entries


@vcr.use_cassette()
def test_get_entries():
    """Reads from the `test_get_entries` cassette and processes the entries. Tests that multiple
    pages get read correctly.

    """
    entries = get_entries()
    assert len(entries) == 1078
    assert entries[0]['cost'] == '39.00'
