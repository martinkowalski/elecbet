"""Test Poll functionality of from_csv.

Only special cases and error catching are tested here. Regular cases are covered by
end-to-end tests.
"""

import datetime as dt
import pytest
from src.polls import from_csv, Poll

FILENAME = 'testdata.csv'

# pylint: disable=missing-docstring

@pytest.fixture(name='make_tmp_csv')
def make_tmp_csv_fixture(tmp_path):
    def create(content: str) -> str:
        file_path = tmp_path / 'testdata.csv'
        file_path.write_text(content)
        return str(file_path)
    return create

@pytest.mark.parametrize("missg_col,content", [
    ("date", "pollster,not_sample_date,sample_size,a,b\nX,2025-02-10,800,0.60,0.30"),
    ("size", "pollster,sample_date,not_sample_size,a,b\nX,2025-02-10,800,0.60,0.30",)
])
def test_raise_on_missing_column(make_tmp_csv, missg_col, content):
    with pytest.raises(ValueError, match=missg_col):
        from_csv(make_tmp_csv(content))

def test_raise_on_missing_values(make_tmp_csv):
    pass

def test_missing_polls(make_tmp_csv):
    content = "pollster,sample_date,sample_size,a,b"
    polls = from_csv(make_tmp_csv(content))
    assert not polls

def test_no_parties(make_tmp_csv):
    content = "pollster,sample_date,sample_size\nX,2025-02-10,800\nY,2025-02-15,600"
    polls = from_csv(make_tmp_csv(content))
    assert polls[0].parties == polls[1].parties == [Poll.OTHERS_KEY]
    assert polls[0].shares == polls[1].shares == 1.0

def test_mixed_case_header(make_tmp_csv):
    content = "Pollster,Sample_Date,SAMPLE_SIZE,a,b,OtHeRs\nX,2025-02-10,800,0.60,0.30,0.10"
    polls = from_csv(make_tmp_csv(content))
    assert polls[0].pollster == "X"
    assert polls[0].parties == ["a", "b", Poll.OTHERS_KEY]

def test_containing_whitespaces_and_empty_lines(make_tmp_csv):
    content = '\n'.join(["  pollster ,sample_date, sample_size     ,  a a , aa, a   a ",
                         "    ",
                         "X,          2025-02-10, 800 , 0.60,0.30, 0.01",
                         "",
                         "     name with spaces , 2025-02-15 , 600 , 0.75 , 0.20, 0.01 ",
                         "    ",
                         ""])
    polls = from_csv(make_tmp_csv(content))
    assert len(polls) == 2
    assert polls[0].sample_date == dt.date(2025, 2, 10)
    assert polls[0].sample_size == 800.0
    assert polls[0].parties == polls[1].parties == ["a a", "aa", "a   a", Poll.OTHERS_KEY]
    assert polls[0].shares == pytest.approx([0.60, 0.30, 0.01, 0.09])
    assert polls[0].pollster == "X"
    assert polls[1].pollster == "name with spaces"

def test_differently_capitalized_parties(make_tmp_csv):
    content = "pollster,sample_date,sample_size,party_a,party_A\nX,2025-02-10,800,0.60,0.30"
    polls = from_csv(make_tmp_csv(content))
    assert polls[0].parties == ['party_a', 'party_A', Poll.OTHERS_KEY]

def test_raise_on_duplicate_parties(make_tmp_csv):
    content = "pollster,sample_date,sample_size,a,b,a\nX,2025-02-10,800,0.60,0.30,0.01"
    with pytest.raises(ValueError, match="duplicate party names"):
        from_csv(make_tmp_csv(content))
