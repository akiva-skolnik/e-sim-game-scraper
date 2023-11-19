# e-sim-scraper
Unofficial scraper for [e-sim](https://luxia.e-sim.org/) game

## Installation
```bash
pip install e-sim-game-scraper
```

## Usage

```python
from e_sim_game_scrapper import EsimScraper

# or from e_sim_game_scrapper.EsimScraper import get_page_data

# Example 1
link = "https://luxia.e-sim.org/battleDrops.html?id=40000&showSpecialItems=yes"
result = EsimScraper.get_page_data(link)

# Example 2 (locked page)
# if you already have a tree (fromstring object):
tree = your_get_tree(link)

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

