import json
from pathlib import Path

import pytest

from agent.schemas import AppSeed
from agent.seed import parse_assignment, write_seed

SAMPLE = """\
# Brief

#### 1\\. CRM and Sales

|
#

 |

App

 |

Website / hint

 |
| --- | --- | --- |
|

1

 |

Salesforce

 |

[salesforce.com](http://salesforce.com/)

 |
|

2

 |

Twenty

 |

[twenty.com](http://twenty.com/) (open-source CRM)

 |
#### 2\\. Support and Helpdesk

|

11

 |

Freshdesk

 |

[freshdesk.com](https://freshdesk.com/)

 |
|

12

 |

Fathom

 |

fathom.video

 |
|

13

 |

Consensus

 |

consensus.app (OAuth requested)

 |
"""


def test_parse_rows_with_links_and_plain_domains() -> None:
    with pytest.raises(ValueError):
        parse_assignment(SAMPLE)


def test_parse_full_assignment() -> None:
    source = Path(__file__).resolve().parent.parent / "composioassignment.md"
    if not source.exists():
        pytest.skip("assignment markdown not present in repo (by design)")
    seeds = parse_assignment(source.read_text())
    assert len(seeds) == 100
    assert [s.id for s in seeds] == list(range(1, 101))
    salesforce = seeds[0]
    assert salesforce.app == "Salesforce"
    assert salesforce.category == "CRM and Sales"
    assert salesforce.domain == "salesforce.com"
    assert salesforce.url == "http://salesforce.com/"
    twenty = next(s for s in seeds if s.app == "Twenty")
    assert twenty.hint == "open-source CRM"
    fathom = next(s for s in seeds if s.app == "Fathom")
    assert fathom.domain == "fathom.video"
    consensus = next(s for s in seeds if s.app == "Consensus")
    assert "OAuth requested" in consensus.hint
    for seed in seeds:
        assert "[" not in seed.app and "http" not in seed.app, seed
    assert next(s for s in seeds if s.id == 76).app == "Monday.com"
    assert next(s for s in seeds if s.id == 37).app == "systeme.io"


def test_categories_cover_all_ten() -> None:
    source = Path(__file__).resolve().parent.parent / "composioassignment.md"
    if not source.exists():
        pytest.skip("assignment markdown not present in repo (by design)")
    seeds = parse_assignment(source.read_text())
    categories = {s.category for s in seeds}
    assert len(categories) == 10
    for category in categories:
        assert sum(1 for s in seeds if s.category == category) == 10


def test_write_seed_roundtrip(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parent.parent / "composioassignment.md"
    if not source.exists():
        pytest.skip("assignment markdown not present in repo (by design)")
    out = tmp_path / "apps.json"
    seeds = write_seed(source, out)
    loaded = [AppSeed.model_validate(row) for row in json.loads(out.read_text())]
    assert loaded == seeds


def test_partial_sample_raises_on_incomplete_set() -> None:
    rows = "\n".join(
        f"|\n\n{i}\n\n |\n\nApp{i}\n\n |\n\n[app{i}.com](http://app{i}.com/)\n\n |"
        for i in range(1, 101)
    )
    doc = f"#### 1\\. Cat One\n\n{rows}\n"
    seeds = parse_assignment(doc)
    assert len(seeds) == 100
    assert all(s.category == "Cat One" for s in seeds)
