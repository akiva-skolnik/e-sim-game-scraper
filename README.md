# E-sim Scraper

Unofficial scraper for the [e-sim](https://luxia.e-sim.org/) browser game.

## Installation

```bash
pip install -U e-sim-game-scraper
```

## Usage

```python
from e_sim_game_scrapper import EsimScraper

# or from e_sim_game_scrapper.EsimScraper import get_page_data

# Example 1
link = "https://luxia.e-sim.org/battleDrops.html?id=1&showSpecialItems=yes"
result = EsimScraper.get_page_data(link)
# >>> {'pages': 2, 'drops': [{'nick': 'Taturuski', 'item': 'Bandage size A', 'citizen_id': 912}, 
# >>>                        {'nick': 'Sverlio77_77', 'item': 'Bandage size C', 'citizen_id': 307}, ...]}

# Example 2 (locked page)
import requests
from lxml.html import fromstring

tree = fromstring(requests.get(link).text)  # this is a locked page, so you actually have to log-in first.
link = "https://luxia.e-sim.org/showShout.html?id=1"
result = EsimScraper.get_page_data(link, tree)
# or call the function directly:
result = EsimScraper.showShout(tree)
```

### List of supported base-links / functions (alphabetical order):

- achievement
- article
- auction
- battleDrops
- battles
- battlesByWar
- citizenStatistics
- coalitionStatistics
- companiesForSale
- congressElections
- countryEconomyStatistics
- countryPoliticalStatistics
- countryStatistics
- events
- jobMarket
- law
- monetaryMarket
- newCitizenStatistics
- newCitizens
- news
- newspaper
- newspaperStatistics
- party
- partyStatistics
- presidentalElections
- productMarket
- profile
- region
- showShout
- stockCompany
- stockCompanyMoney
- stockCompanyProducts

(**Note**: not all of them are tested, some of them may not work properly, as those are dynamic pages that may change over time.)  
There are tests for most of them locally, but they are not included in the package for now.

## Support the Project:

The development and maintenance of this bot are ongoing. If you find it valuable, please consider supporting it through
a donation:

- [Buy Me a Coffee](https://www.buymeacoffee.com/ripEsim)
- [Patreon](https://www.patreon.com/ripEsim)

Your contributions will help ensure the bot's continued improvement and availability for the e-Sim community.
