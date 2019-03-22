import vcr

from service import get_entries


@vcr.use_cassette()
def test_get_entries():
    """Reads from the `test_get_entries` cassette and processes the entries. Tests that multiple
    pages get read, invalid entries are discarded, and `event_date` is split into its constituent
    parts.

    """
    entries = get_entries()
    assert len(entries) == 39
    assert entries[0]['start_date'] == '2019-03-26'