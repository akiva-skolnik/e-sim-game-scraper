from datetime import date, timedelta
from typing import Union
import inspect

from .utils import *  # relative import


def get_page_data(link: str, tree: fromstring = None) -> Union[dict, list]:
    """Gets the data from the link/tree and returns it as a dictionary or a list of dictionaries"""
    if not tree:
        if "statistics.html" in link:
            link = redirect_statistics(link)
        tree = get_tree(link)
    function_name = link.split("/")[-1].split(".")[0]
    try:
        function = globals()[function_name]
    except KeyError:
        return {"error": "function not found"}
    num_args = function.__code__.co_argcount
    if num_args == 1:
        return function(tree)
    elif num_args == 2:
        return function(tree, link)


def get_supported_functions() -> list:
    return [func.__name__ for func in globals().values() if inspect.isfunction(func) and func.__module__ == __name__
            and func.__name__ not in ("get_page_data", "get_supported_functions")]


def article(tree: fromstring) -> dict:
    posted = " ".join(tree.xpath('//*[@class="mobile_article_preview_width_fix"]/text()')[0].split()[1:-1])
    title = tree.xpath('//*[@class="articleTitle"]/text()')[0]
    subs, votes = [int(x.strip()) for x in tree.xpath('//*[@class="bigArticleTab"]/text()')]
    author_name, newspaper_name = tree.xpath('//*[@class="mobileNewspaperStatus"]/a/text()')
    author_id = int(get_ids_from_path(tree, '//*[@id="mobileNewspaperStatusContainer"]/div[1]/a')[0])
    newspaper_id = int(tree.xpath('//*[@class="mobileNewspaperStatus"]/a/@href')[-1].split("=")[1])
    result = {"posted": posted, "title": title, "author": author_name.strip(), "author_id": author_id, "votes": votes,
              "newspaper": newspaper_name, "newspaper_id": newspaper_id, "subs": subs}
    return result


def auction(tree: fromstring) -> dict:
    seller = tree.xpath("//div[1]//table[1]//tr[2]//td[1]//a/text()")[0]
    buyer = tree.xpath("//div[1]//table[1]//tr[2]//td[2]//a/text()") or ["None"]
    item = tree.xpath("//*[@id='esim-layout']//div[1]//tr[2]//td[3]/b/text()")
    if not item:
        item = [x.strip() for x in tree.xpath("//*[@id='esim-layout']//div[1]//tr[2]//td[3]/text()") if x.strip()]
    price = float(tree.xpath("//div[1]//table[1]//tr[2]//td[4]//b//text()")[0])
    bidders = int(tree.xpath('//*[@id="esim-layout"]//div[1]//table//tr[2]//td[5]/b')[0].text)
    time1 = tree.xpath('//*[@id="esim-layout"]//div[1]//table//tr[2]//td[6]/span/text()')
    if not time1:
        time1 = [x.strip() for x in tree.xpath('//*[@id="esim-layout"]//div[1]//table//tr[2]//td[6]/text()') if
                 x.strip()]
        reminding_seconds = -1
    else:
        time1 = [int(x) for x in time1[0].split(":")]
        reminding_seconds = time1[0] * 60 * 60 + time1[1] * 60 + time1[2]
        time1 = [f'{time1[0]:02d}:{time1[1]:02d}:{time1[2]:02d}']
    result = {"seller": seller.strip(), "buyer": buyer[0].strip(), "item": item[0],
              "price": price, "time": time1[0], "bidders": bidders, "reminding_seconds": reminding_seconds}
    return result


def showShout(tree: fromstring) -> dict:
    shout = [x.strip() for x in tree.xpath('//*[@class="shoutContainer"]//div//div[1]//text()') if x.strip()]
    shout = "\n".join([x.replace("★", "") for x in shout]).strip()
    author = tree.xpath('//*[@class="shoutAuthor"]//a/text()')[0].strip()
    posted = tree.xpath('//*[@class="shoutAuthor"]//b')[0].text
    result = {"body": shout, "author": author, "posted": posted.replace("posted ", "")}
    return result


def law(tree: fromstring) -> dict:
    time1 = tree.xpath('//*[@id="esim-layout"]//script[3]/text()')[0]
    time1 = [i.split(");\n")[0] for i in time1.split("() + ")[1:]]
    if int(time1[0]) < 0:
        time1 = "Voting finished"
    else:
        time1 = f'{int(time1[0]):02d}:{int(time1[1]):02d}:{int(time1[2]):02d}'
    proposal = " ".join([x.strip() for x in tree.xpath('//table[1]//tr[2]//td[1]//div[2]//text()')]).strip()
    by = tree.xpath('//table[1]//tr[2]//td[3]//a/text()')[0]
    yes = [x.strip() for x in tree.xpath('//table[2]//td[2]//text()') if x.strip()][0]
    no = [x.strip() for x in tree.xpath('//table[2]//td[3]//text()') if x.strip()][0]
    time2 = tree.xpath('//table[1]//tr[2]//td[3]//b')[0].text
    result = {"law_proposal": proposal, "proposed_by": by.strip(), "proposed": time2,
              "remaining_time" if "Voting finished" not in time1 else "status": time1, "yes": int(yes), "no": int(no)}
    return result


def congressElections(tree: fromstring) -> dict:
    country = tree.xpath('//*[@id="countryId"]//option[@selected="selected"]')[0].text
    country_id = int(tree.xpath('//*[@id="countryId"]//option[@selected="selected"]/@value')[0])
    date = tree.xpath('//*[@id="date"]//option[@selected="selected"]')[0].text
    candidates = tree.xpath("//tr//td[2]//a/text()")
    candidates_ids = get_ids_from_path(tree, "//tr//td[2]//a")
    parties = tree.xpath("//tr//td[4]//div/a/text()")
    parties_links = tree.xpath("//tr//td[4]//div/a/@href")
    votes = [x.replace("-", "0").strip() for x in tree.xpath("//tr[position()>1]//td[5]//text()")
             if x.strip()] or [0] * len(candidates)

    result = {"country": country, "country_id": country_id, "date": date, "candidates": []}
    for candidate, candidate_id, vote, party_name, party_id in zip(
            candidates, candidates_ids, votes, parties, parties_links):
        result["candidates"].append(
            {"candidate": candidate.strip(), "candidate_id": int(candidate_id), "votes": int(vote.strip()),
             "party_name": party_name, "party_id": int(party_id.split("id=")[1])})
    return result


def presidentalElections(tree: fromstring) -> dict:
    country = tree.xpath('//*[@id="countryId"]//option[@selected="selected"]')[0].text
    country_id = int(tree.xpath('//*[@id="countryId"]//option[@selected="selected"]/@value')[0])
    date = tree.xpath('//*[@id="date"]//option[@selected="selected"]')[0].text
    candidates = tree.xpath("//tr//td[2]//a/text()")
    candidates_ids = get_ids_from_path(tree, "//tr//td[2]//a")
    votes = [x.replace("-", "0").strip() for x in tree.xpath("//tr[position()>1]//td[4]//text()")
             if x.strip()] or [0] * len(candidates)
    result = {"country": country, "country_id": country_id, "date": date, "candidates": []}
    for candidate, vote, candidate_id in zip(candidates, votes, candidates_ids):
        result["candidates"].append(
            {"candidate": candidate.strip(), "votes": int(vote.strip()), "candidate_id": int(candidate_id)})
    return result


def battleDrops(tree: fromstring, link: str) -> dict:
    last_page = tree.xpath("//ul[@id='pagination-digg']//li[last()-1]//@href") or ['page=1']
    last_page = int(last_page[0].split('page=')[1])
    result = {"pages": last_page, "drops": []}
    if "showSpecialItems" in link:
        nicks = tree.xpath("//tr[position()>1]//td[2]//a/text()")
        items = [x.strip() for x in tree.xpath("//tr[position()>1]//td[1]//text()") if x.strip()]
        ids = get_ids_from_path(tree, "//tr[position()>1]//td[2]//a")
        for nick, item, citizen_id in zip(nicks, items, ids):
            result["drops"].append({"nick": nick.strip(), "item": item, "citizen_id": int(citizen_id)})
    else:
        nicks = tree.xpath("//tr[position()>1]//td[4]//a/text()")
        qualities = tree.xpath("//tr[position()>1]//td[2]/text()")
        items = tree.xpath("//tr[position()>1]//td[3]/text()")
        ids = get_ids_from_path(tree, "//tr[position()>1]//td[4]//a")
        for nick, quality, item, citizen_id in zip(nicks, qualities, items, ids):
            result["drops"].append({"nick": nick.strip(), "citizen_id": int(citizen_id), "item": item.strip(),
                                    "quality": int(quality.replace("Q", ""))})
    return result


def jobMarket(tree: fromstring) -> dict:
    country = tree.xpath('//*[@id="countryId"]//option[@selected="selected"]')[0].text
    country_id = int(tree.xpath('//*[@id="countryId"]//option[@selected="selected"]/@value')[0])
    employers = tree.xpath('//*[@id="esim-layout"]//td[1]/a/text()')
    companies = tree.xpath('//*[@id="esim-layout"]//td[2]/a/text()')
    companies_link = tree.xpath('//*[@id="esim-layout"]//td[2]/a/@href')
    company_types = []
    qualities = []
    products = tree.xpath('//*[@id="esim-layout"]//td[3]/div/div/img/@src')
    for p in chunker(products, 2):
        product, quality = [x.split("/")[-1].split(".png")[0] for x in p]
        product = product.replace("Defense System", "Defense_System").strip()
        quality = quality.replace("q", "").strip()
        company_types.append(product)
        qualities.append(int(quality))
    skills = tree.xpath('//*[@id="esim-layout"]//tr[position()>1]//td[4]/text()')
    salaries = tree.xpath('//*[@id="esim-layout"]//td[5]/b/text()')
    result = {"country": country, "country_id": country_id, "offers": []}
    for employer, company, company_link, company_type, quality, skill, salary in zip(
            employers, companies, companies_link, company_types, qualities, skills, salaries):
        result["offers"].append(
            {"employer": employer.strip(), "company": company, "company_id": int(company_link.split("?id=")[1]),
             "company_type": company_type, "company_quality": int(quality),
             "minimal_skill": int(skill), "salary": float(salary)})
    result["cc"] = tree.xpath('//*[@id="esim-layout"]//tr[2]//td[5]/text()')[-1].strip() if result["offers"] else ""
    return result


def newCitizens(tree: fromstring) -> dict:
    country = tree.xpath('//*[@id="countryId"]//option[@selected="selected"]')[0].text
    country_id = int(tree.xpath('//*[@id="countryId"]//option[@selected="selected"]/@value')[0])
    nicks = tree.xpath('//td[1]/a/text()')
    levels = tree.xpath('//tr[position()>1]//td[2]/text()')
    experiences = tree.xpath('//tr[position()>1]//td[3]/text()')
    registered = tree.xpath('//tr[position()>1]//td[4]/text()')
    locations = tree.xpath('//tr[position()>1]//td[5]/a/text()')
    location_links = tree.xpath('//td[5]/a/@href')
    ids = get_ids_from_path(tree, "//td[1]/a")
    result = {"country": country, "country_id": country_id, "new_citizens": []}
    for nick, level, experience, registered, location, location_link, citizen_id in zip(
            nicks, levels, experiences, registered, locations, location_links, ids):
        result["new_citizens"].append(
            {"nick": nick, "level": int(level.strip()), "experience": int(experience.strip()),
             "registered": registered.strip(), "region": location, "location_id": int(location_link.split("?id=")[1]),
             "citizen_id": int(citizen_id)})
    return result


def region(tree: fromstring) -> dict:
    owner = tree.xpath('//*[@id="esim-layout"]//div[1]//tr[2]//td[1]//span')[0].text
    rightful_owner = tree.xpath('//*[@id="esim-layout"]//div[1]//tr[2]//td[2]//span')[0].text
    region_name = tree.xpath('//*[@id="esim-layout"]//h1')[0].text.replace("Region ", "")
    try:
        resource_type = tree.xpath('//*[@id="esim-layout"]//div[1]//tr[2]//td[3]/div/div/img/@src')[0].split(
            "/")[-1].split(".png")[0]
    except:
        resource_type = "No resources"
    resource = tree.xpath('//*[@id="esim-layout"]//div[1]//tr[2]//td[3]/b')
    resource = resource[0].text if resource else "No resources"
    population = tree.xpath('//*[@id="esim-layout"]//div[1]//tr[2]//td[4]/b')[0].text
    active_companies, all_companies = tree.xpath('//*[@id="esim-layout"]//div[1]//tr[2]//td[5]/b')[0].text.split()

    is_occupied = tree.xpath('//*[@id="esim-layout"]//div[2]//b[1]/text()')
    base_div = 3 if len(is_occupied) == 1 else 2
    industry = tree.xpath(f'//*[@id="esim-layout"]//div[{base_div}]//table[1]//b[1]/text()')
    industry = dict(zip(industry[::2], [float(x) for x in industry[1::2]]))
    companies_type = tree.xpath('//*[@id="esim-layout"]//table[2]//td[1]/b/text()')
    total_companies = [x.strip() for x in tree.xpath('//*[@id="esim-layout"]//table[2]//tr[position()>1]//td[2]/text()')
                       if x.strip()]
    values = tree.xpath('//*[@id="esim-layout"]//table[2]//td[3]/b/text()')
    penalties = tree.xpath('//*[@id="esim-layout"]//table[2]//tr[position()>1]//td[4]/text()') or ["100%"] * len(values)

    active = [{"type": company_type, "total_companies": int(total_companies.strip()), "value": float(value),
               "penalty": penalty.strip()}
              for company_type, total_companies, value, penalty in zip(
            companies_type, total_companies, values, penalties)]

    rounds = tree.xpath('//*[@id="esim-layout"]//table[2]//td[2]/b/text()')
    buildings = tree.xpath('//*[@id="esim-layout"]//table[2]//td[1]/div/div/img/@src')
    building_places = {}
    for round_number, p in zip(rounds, chunker(buildings, 2)):
        building, quality = [x.split("/")[-1].split(".png")[0] for x in p]
        building = building.replace("Defense System", "Defense_System").strip()
        building_places[int(round_number)] = f"{quality.strip().upper()} {building}"

    result = {"region": region_name, "active_companies_stats": active,
              "buildings": [{"round": k, "building": v} for k, v in building_places.items()],
              "industry": [{"company": k, "total_value": v} for k, v in industry.items()], "current_owner": owner,
              "rightful_owner": rightful_owner, "resource": resource_type, "resource_richness": resource,
              "population": int(population),
              "active_companies": int(active_companies),
              "total_companies": int(all_companies.replace("(", "").replace(")", ""))}
    return result


def monetaryMarket(tree: fromstring) -> dict:
    sellers = tree.xpath("//*[@class='seller']/a/text()")
    if not sellers:
        return {"error": "no offers", "offers": []}
    buy = tree.xpath("//*[@class='buy']/button")[0].attrib['data-buy-currency-name']
    sell = tree.xpath("//*[@class='buy']/button")[0].attrib['data-sell-currency-name']
    seller_ids = [int(x.split("?id=")[1]) for x in tree.xpath("//*[@class='seller']/a/@href")]
    amounts = tree.xpath("//*[@class='amount']//b/text()")
    ratios = tree.xpath("//*[@class='ratio']//b/text()")
    offers_ids = [int(x.attrib['data-id']) for x in tree.xpath("//*[@class='buy']/button")]
    result = {"buy": buy, "sell": sell, "offers": []}
    for seller, seller_id, amount, ratio, offer_id in zip(sellers, seller_ids, amounts, ratios, offers_ids):
        result["offers"].append({"seller": seller.strip(), "seller_id": seller_id,
                                 "amount": float(amount), "ratio": float(ratio), "offer_id": offer_id})
    return result


def stockCompany(tree: fromstring) -> dict:
    sc_name = tree.xpath("//span[@class='big-login']")[0].text
    ceo = (tree.xpath('//*[@id="partyContainer"]//div//div[1]//div//div[1]//div[2]/a/text()') or ["No CEO"])[0].strip()
    ceo_status = tree.xpath('//*[@id="partyContainer"]//div//div[1]//div//div[1]//div[2]//a/@style') or [
        "Active" if ceo != "No CEO" else ""]
    ceo_status = ceo_status[0].replace("color: #f00; text-decoration: line-through;", "Banned").replace(
        "color: #888;", "Inactive")
    main = [float(x) for x in tree.xpath('//*[@class="muColEl"]//b/text()')]
    try:
        price = tree.xpath('//*[@id="esim-layout"]//tr//td[2]//div[1]//table[1]//td[2]/b/text()')
        price = [float(x) for x in price]
        stock = tree.xpath('//*[@id="esim-layout"]//tr//td[2]//div[1]//table[1]//td[1]/b/text()')
        stock = [int(x) for x in stock]
    except:
        price, stock = [], []
    offers = [{"amount": stock, "price": price} for stock, price in zip(stock, price)]
    try:
        last_transactions_amount = tree.xpath('//*[@id="esim-layout"]//tr//td[2]//div[1]//table[3]//td[1]/b/text()')
        last_transactions_price = tree.xpath('//*[@id="esim-layout"]//tr//td[2]//div[1]//table[3]//td[2]/b/text()')
        last_transactions_time = tree.xpath(
            '//*[@id="esim-layout"]//tr//td[2]//div[1]//table[3]//tr[position()>1]//td[3]/text()')
    except:
        last_transactions_amount, last_transactions_price, last_transactions_time = [], [], []
    header = ["total_shares", "total_value", "price_per_share", "daily_trade_value", "shareholders", "companies",
              # main
              "sc_name", "ceo", "ceo_status", "offers"]
    data = main + [sc_name, ceo, ceo_status, offers]
    last_transactions = [{"amount": int(a.strip()), "price": float(b.strip()), "time": c.strip()} for a, b, c in zip(
        last_transactions_amount, last_transactions_price, last_transactions_time)]
    result = dict(zip(header, data))
    result["last_transactions"] = last_transactions
    return result


def stockCompanyProducts(tree: fromstring) -> dict:
    result = {}
    amount = [int(x.strip()) for x in tree.xpath('//*[@id="esim-layout"]//center//div//div//div[1]/text()')]
    products = [x.split("/")[-1].split(".png")[0] for x in
                tree.xpath('//*[@id="esim-layout"]//center//div//div//div[2]//img[1]/@src')]
    for index, product in enumerate(products):
        quality = tree.xpath(f'//*[@id="esim-layout"]//center//div//div[{index + 1}]//div[2]//img[2]/@src')
        if "Defense System" in product:
            product = product.replace("Defense System", "Defense_System")
        if quality:
            products[index] = f'{quality[0].split("/")[-1].split(".png")[0].upper()} {product}'
    result["storage"] = [{"product": product, "amount": amount} for product, amount in zip(products, amount)]

    amount = [int(x.strip()) for x in tree.xpath('//*[@id="esim-layout"]//div[2]//table//tr//td[3]/text()')[1:]]
    gross_price = tree.xpath('//*[@id="esim-layout"]//div[2]//table//tr//td[4]/b/text()')
    coin = [x.strip() for x in tree.xpath('//*[@id="esim-layout"]//div[2]//table//tr//td[4]/text()')[1:] if x.strip()]
    net_price = tree.xpath('//*[@id="esim-layout"]//div[2]//table//tr//td[5]/b/text()')
    products = [x.split("/")[-1].split(".png")[0] for x in
                tree.xpath('//*[@id="esim-layout"]//div[2]//table//tr//td[1]//img[1]/@src')]
    for index, product in enumerate(products):
        quality = tree.xpath(f'//*[@id="esim-layout"]//div[2]//table//tr[{index + 2}]//td[1]//img[2]/@src')
        if "Defense System" in product:
            product = product.replace("Defense System", "Defense_System")
        if quality:
            products[index] = f'{quality[0].split("/")[-1].split(".png")[0].upper()} {product}'
    result["offers"] = []
    for product, amount, gross_price, coin, net_price in zip(products, amount, gross_price, coin, net_price):
        result["offers"].append(
            {"product": product, "amount": amount, "gross_price": float(gross_price),
             "coin": coin, "net_price": float(net_price)})
    return result


def stockCompanyMoney(tree: fromstring) -> dict:
    coins = [x.strip() for x in tree.xpath('//*[@id="esim-layout"]//div[3]//div/text()') if x.strip()]
    stock = tree.xpath('//*[@id="esim-layout"]//div[3]//div//b/text()')
    result = {"storage": [{k: float(v) for k, v in zip(coins, stock)}]}

    amounts = [float(x) for x in tree.xpath('//*[@id="esim-layout"]//div[4]//table//tr/td[2]/b/text()')]
    coins = [x.strip() for x in tree.xpath('//*[@id="esim-layout"]//div[4]//table//tr/td[2]/text()') if x.strip()][1:]
    ratios = [float(x) for x in tree.xpath('//*[@id="esim-layout"]//div[4]//table//tr/td[3]/b/text()')]
    offer_ids = [int(x.value) for x in tree.xpath('//*[@id="esim-layout"]//div[4]//table//tr/td[4]//form//input[2]')]
    result["offers"] = [{"amount": amount, "coin": coin, "ratio": ratio, "offer_id": offer_id} for
                        amount, coin, ratio, offer_id in zip(
            amounts, coins, ratios, offer_ids)]
    return result


def achievement(tree: fromstring) -> dict:
    last_page = tree.xpath("//ul[@id='pagination-digg']//li[last()-1]//@href") or ['page=1']
    last_page = int(last_page[0].split('page=')[1])
    ids = get_ids_from_path(tree, '//*[@id="esim-layout"]//div[3]//div/a')
    nicks = [x.strip() for x in tree.xpath('//*[@id="esim-layout"]//div[3]//div/a/text()')]
    category, achieved_by = [x.split(":")[1].strip() for x in
                             tree.xpath('//*[@id="esim-layout"]//div[1]//div[2]/text()') if x.strip()]
    description = tree.xpath('//*[@class="foundation-style columns column-margin-vertical help"]/i/text()')[0].strip()
    players = [{"citizen_id": int(citizen_id), "nick": nick} for citizen_id, nick in zip(ids, nicks)]
    result = {"description": description, "category": category, "achieved_by": achieved_by, "players": players,
              "pages": last_page}
    return result


def countryEconomyStatistics(tree: fromstring) -> dict:
    country = tree.xpath('//*[@id="countryId"]//option[@selected="selected"]')[0].text
    country_id = int(tree.xpath('//*[@id="countryId"]//option[@selected="selected"]/@value')[0])
    links = [int(x.split("id=")[1]) for x in tree.xpath('//*[@id="esim-layout"]//table[1]//td[1]/a/@href')]
    regions = tree.xpath('//*[@id="esim-layout"]//table[1]//td[1]/a/text()')
    regions = [dict(zip(links, regions))]
    population = [x.strip().replace(":", "").replace(" ", "_").lower() for x in
                  tree.xpath('//*[@id="esim-layout"]//div[2]//div[2]//table//tr//td/text()') if x.strip()]
    minimal_salary = tree.xpath('//*[@id="esim-layout"]//div[2]//table//tr[6]//td[2]/b')[0].text
    population[-1] = minimal_salary
    population = dict(zip(population[::2], [float(x) for x in population[1::2]]))
    treasury_keys = [x.strip() for x in
                     tree.xpath('//*[@id="esim-layout"]//div[2]//div[5]//table//tr[position()>1]//td/text()') if
                     x.strip()]
    treasury_values = tree.xpath('//*[@id="esim-layout"]//div[2]//div[5]//table//tr[position()>1]//td/b/text()')
    treasury = [{k: float(v) for k, v in zip(treasury_keys, treasury_values)}]
    table = [x.strip() for x in tree.xpath('//*[@id="esim-layout"]//div[2]//div[4]//table//tr//td/text()')]
    columns = 5
    taxes = {table[columns:][i]: table[columns:][i + 1:i + columns] for i in
             range(0, len(table[columns:]) - columns, columns)}
    taxes_list = [{**dict(zip(table[1:columns], v)), **{"type": k}} for k, v in taxes.items()]
    result = {"country": country, "country_id": country_id, "borders": regions, "treasury": treasury,
              "taxes": taxes_list}
    result.update(population)
    return result


def stockCompanyStatistics(tree: fromstring, link: str) -> dict:
    return citizenStatistics(tree, link)


def citizenStatistics(tree: fromstring, link: str) -> dict:
    citizens = "citizenStatistics" in link
    country = tree.xpath('//*[@id="countryId"]//option[@selected="selected"]')[0].text
    try:
        statistic_type = tree.xpath('//*[@name="statisticType"]//option[@selected="selected"]')[0].text
    except:
        statistic_type = tree.xpath('//*[@name="statisticType"]//option[1]')[0].text
    country_id = int(tree.xpath('//*[@id="countryId"]//option[@selected="selected"]/@value')[0])
    ids = get_ids_from_path(tree, "//td/a")
    nicks = tree.xpath("//td/a/text()")
    countries = tree.xpath("//td[3]/b/text()")
    values = tree.xpath("//tr[position()>1]//td[4]/text()") if citizens else tree.xpath(
        "//tr[position()>1]//td[4]/b/text()")
    for index, parameter in enumerate(values):
        value = ""
        for char in parameter:
            if char in "1234567890.":
                value += char
        if value:
            values[index] = float(value)

    result = {"country": country, "country_id": country_id, "statistic_type": statistic_type,
              ("citizens" if citizens else "stock_companies"): [
                  {"id": int(key_id),
                   "nick" if citizens else "stock_company": nick.strip(),
                   "country": country, statistic_type.lower(): value} for key_id, nick, country, value in
                  zip(ids, nicks, countries, values)]}
    return result


def countryStatistics(tree: fromstring) -> dict:
    statistic_type = tree.xpath('//*[@name="statisticType"]//option[@selected="selected"]')[0].text
    countries = tree.xpath("//td/b/text()")[1:]
    values = tree.xpath("//td[3]/text()")[1:]
    result = {"statistic_type": statistic_type,
              "countries": [{"country": k, statistic_type.lower(): int(v.replace(",", "").strip())} for k, v in
                            zip(countries, values)]}
    return result


def coalitionStatistics(tree: fromstring) -> list:
    result = []
    for tr in range(2, 103):  # First 100
        try:
            coalition_id = int(tree.xpath(f'//tr[{tr}]//td[1]//span'))
            name = tree.xpath(f'//tr[{tr}]//td[2]//span/text()') or ["-"]
            leader = tree.xpath(f'//tr[{tr}]//td[3]/a/text()') or ["-"]
            leader_id = (get_ids_from_path(tree, f'//tr[{tr}]//td[3]/a/@href') or [0])[0]
            members = int(tree.xpath(f'//tr[{tr}]//td[4]//span')[0].text)
            regions = int(tree.xpath(f'//tr[{tr}]//td[5]//span')[0].text)
            citizens = int(tree.xpath(f'//tr[{tr}]//td[6]//span')[0].text)
            dmg = int(tree.xpath(f'//tr[{tr}]//td[7]//span')[0].text.replace(",", ""))
            result.append({"coalition_id": coalition_id, "name": name[0], "leader": leader[0].strip(),
                           "leader_id": int(leader_id),
                           "members": members, "regions": regions, "citizens": citizens, "dmg": dmg})
        except:
            break
    result = sorted(result, key=lambda k: k['dmg'], reverse=True)
    return result


def newCitizenStatistics(tree: fromstring) -> list:
    names = [x.strip() for x in tree.xpath("//tr//td[1]/a/text()")]
    citizen_ids = [int(x.split("?id=")[1]) for x in tree.xpath("//tr//td[1]/a/@href")]
    countries = tree.xpath("//tr//td[2]/span/text()")
    registration_time = [x.strip() for x in tree.xpath("//tr[position()>1]//td[3]/text()[1]")]
    registration_time1 = tree.xpath("//tr//td[3]/text()[2]")
    xp = [int(x) for x in tree.xpath("//tr[position()>1]//td[4]/text()")]
    wep = ["479" in x for x in tree.xpath("//tr[position()>1]//td[5]/i/@class")]
    food = ["479" in x for x in tree.xpath("//tr[position()>1]//td[6]/i/@class")]
    gift = ["479" in x for x in tree.xpath("//tr[position()>1]//td[5]/i/@class")]
    result = []
    for name, citizen_id, country, registration_time, registration_time1, xp, wep, food, gift in zip(
            names, citizen_ids, countries, registration_time, registration_time1, xp, wep, food, gift):
        result.append(
            {"name": name, "citizen_id": citizen_id, "country": country, "registration_time": registration_time,
             "registered": registration_time1[1:-1], "xp": xp, "wep": wep, "food": food, "gift": gift})
    return result


def partyStatistics(tree: fromstring) -> list:
    country = tree.xpath("//tr//td[2]/b/text()")[:50]
    party_name = tree.xpath("//tr//td[3]//div/a/text()")[:50]
    party_id = [int(x.split("?id=")[1]) for x in tree.xpath("//tr//td[3]//div/a/@href")][:50]
    prestige = [int(x) for x in tree.xpath("//tr[position()>1]//td[4]/text()")][:50]
    elected_cps = [int(x.strip()) if x.strip() else 0 for x in tree.xpath("//tr[position()>1]//td[5]/text()")][:50]
    elected_congress = [int(x.strip()) if x.strip() else 0 for x in tree.xpath("//tr[position()>1]//td[6]/text()")][:50]
    laws = [int(x.strip()) if x.strip() else 0 for x in tree.xpath("//tr[position()>1]//td[7]/text()")][:50]
    members = [int(x) for x in tree.xpath("//tr//td[8]/b/text()")][:50]
    result = []
    for country, party_name, party_id, prestige, elected_cps, elected_congress, laws, members in zip(
            country, party_name, party_id, prestige, elected_cps, elected_congress, laws, members):
        result.append({"country": country, "party": party_name, "party_id": party_id, "prestige": prestige,
                       "elected_cps": elected_cps,
                       "elected_congress": elected_congress, "laws": laws, "members": members})
    return result


def newspaperStatistics(tree: fromstring) -> dict:
    last_page = tree.xpath("//ul[@id='pagination-digg']//li[last()-1]//@href") or ['page=1']
    last_page = int(last_page[0].split('page=')[1])
    result = {"pages": last_page, "newspapers": []}

    indexes = [int(x.strip()) for x in tree.xpath("//tr[position()>1]//td[1]/text()")]
    redactors = [x.strip() for x in tree.xpath("//tr//td[2]/a/text()")]
    redactor_ids = get_ids_from_path(tree, "//tr//td[2]/a")
    newspaper_names = tree.xpath("//tr//td[3]/span/a/text()")
    newspaper_ids = [int(x.split("?id=")[1]) for x in tree.xpath("//tr//td[3]/span/a/@href")]
    subs = [int(x) for x in tree.xpath("//tr[position()>1]//td[4]/b/text()")]
    for index, redactor, redactor_id, newspaper_name, newspaper_id, sub in zip(
            indexes, redactors, redactor_ids, newspaper_names, newspaper_ids, subs):
        result["newspapers"].append({"index": index, "redactor": redactor, "redactor_id": int(redactor_id),
                                     "newspaper": newspaper_name, "newspaper_id": newspaper_id, "subs": sub})
    return result


def news(tree: fromstring) -> dict:
    country = tree.xpath('//*[@id="country"]//option[@selected="selected"]')[0].text
    country_id = int(tree.xpath('//*[@id="country"]//option[@selected="selected"]/@value')[0])
    news_type = tree.xpath('//*[@id="newsType"]//option[@selected="selected"]')[0].text
    votes = [int(x.strip()) for x in tree.xpath('//tr//td//div[1]/text()') if x.strip()]
    titles = tree.xpath('//tr//td//div[2]/a/text()')
    links = [int(x.split("?id=")[1]) for x in tree.xpath('//tr//td//div[2]/a/@href')]
    posted = tree.xpath('//tr//td//div[2]//text()[preceding-sibling::br]')
    types, posted = [x.replace("Article type: ", "").strip() for x in posted[1::2]], \
        [x.replace("Posted", "").strip() for x in posted[::2]]
    newspaper_names = [x.strip() for x in tree.xpath('//*[@id="esim-layout"]//table//tr//td//div[3]//div/a[1]/text()')]
    newspaper_id = [int(x.split("?id=")[1]) for x in
                    tree.xpath('//*[@id="esim-layout"]//table//tr//td//div[3]//div/a[1]/@href')]
    result = {"country": country, "country_id": country_id, "news_type": news_type, "articles": []}
    for title, link, vote, posted, article_type, newspaper_name, newspaper_id in zip(
            titles, links, votes, posted, types, newspaper_names, newspaper_id):
        result["articles"].append(
            {"title": title, "article id": link, "votes": vote, "posted": posted, "type": article_type,
             "newspaper_name": newspaper_name, "newspaper_id": newspaper_id})
    return result


def events(tree: fromstring) -> dict:
    last_page = tree.xpath("//ul[@id='pagination-digg']//li[last()-1]//@href") or ['page=1']
    last_page = int(last_page[0].split('page=')[1])
    country = tree.xpath('//*[@id="country"]//option[@selected="selected"]')[0].text
    country_id = int(tree.xpath('//*[@id="country"]//option[@selected="selected"]/@value')[0])
    events_type = tree.xpath('//*[@id="eventsType"]//option[@selected="selected"]')[0].text
    titles = [x.text_content().replace("\n\xa0 \xa0 \xa0 \xa0", "").replace("  ", " ").strip() for x in
              tree.xpath('//tr//td//div[2]')]
    titles = [x for x in titles if x]
    icons = [x.split("/")[-1].replace("Icon.png", "") for x in tree.xpath('//tr//td//div[1]//img//@src')]
    icons = [x if ".png" not in x else "" for x in icons]
    links = tree.xpath('//tr//td//div[2]/a/@href')
    result = {"country": country, "country_id": country_id, "pages": last_page, "events_type": events_type,
              "events": []}
    for title, link, icon in zip(titles, links, icons):
        result["events"].append(
            {"event": " ".join(title.split("  ")[:-1]).strip(), "time": title.split("  ")[-1].strip(), "link": link,
             "icon": icon})
    return result


def companiesForSale(tree: fromstring) -> list:
    company_ids = [int(x.split("?id=")[1]) for x in tree.xpath('//tr//td[1]//a/@href')]
    company_names = [x.strip() for x in tree.xpath('//tr//td[1]/a/text()')]
    company_types = []
    qualities = []
    products = tree.xpath('//tr//td[2]//div//div//img/@src')
    for p in chunker(products, 2):
        product, quality = [x.split("/")[-1].split(".png")[0] for x in p]
        product = product.replace("Defense System", "Defense_System").strip()
        quality = quality.replace("q", "").strip()
        company_types.append(product)
        qualities.append(int(quality))
    location_names = tree.xpath('//tr//td[3]/b/a/text()')
    countries = tree.xpath('//tr//td[3]/span[last()]/text()')
    location_ids = [int(x.split("?id=")[1]) for x in tree.xpath('//tr//td[3]//a/@href')]
    seller_ids = get_ids_from_path(tree, '//tr//td[4]//a')
    seller_names = [x.replace("\xa0", "") for x in tree.xpath('//tr//td[4]//a/text()')]
    seller_types = tree.xpath('//tr//td[4]//b/text()')
    prices = [float(x.replace(" Gold", "")) for x in tree.xpath('//tr//td[5]//b/text()')]
    offer_ids = [int(x.value) for x in tree.xpath('//tr//td[6]//input[1]')]
    result = []
    for (company_id, company_name, company_types, qualities, location_name, country, location_id, seller_id,
         seller_name, seller_type, price, offer_id) in zip(
        company_ids, company_names, company_types, qualities, location_names, countries, location_ids, seller_ids,
        seller_names, seller_types, prices, offer_ids):
        result.append({"company_id": company_id, "company_name": company_name, "company_type": company_types,
                       "quality": qualities, "location_name": location_name,
                       "country": country, "location_id": location_id, "seller_id": int(seller_id),
                       "seller_name": seller_name,
                       "seller_type": seller_type, "price": price, "offer_id": offer_id})
    return result


def countryPoliticalStatistics(tree: fromstring) -> dict:
    result = {}
    for minister in ["Defense", "Finance", "Social"]:
        ministry = tree.xpath(f'//*[@id="ministryOf{minister}"]//div//div[2]/a[1]/text()')
        try:
            link = int(get_ids_from_path(tree, f'//*[@id="ministryOf{minister}"]//div//div[2]/a[1]')[0])
        except:
            continue
        result["minister_of_" + minister.lower()] = {"id": link, "nick": ministry[0]}

    orders = tree.xpath('//*[@id="presidentBattleOrder"]//@href')
    if len(orders) == 1:
        result["country_order"] = orders[0]
    elif len(orders) == 2:
        result["country_order"] = orders[0]
        result["coalition_order"] = orders[1]
    congress = tree.xpath('//*[@id="congressByParty"]//a/text()')
    congress_links = get_ids_from_path(tree, '//*[@id="congressByParty"]//a')
    result["congress"] = [{"nick": congress.strip(), "id": int(link)} for congress, link in
                          zip(congress, congress_links)]
    coalition = tree.xpath('//*[@id="mobileCountryPoliticalStats"]/span/text()')
    result["coalition_members"] = coalition
    sides = [x.replace("xflagsMedium xflagsMedium-", "").replace("-", " ") for x in
             tree.xpath('//table[1]//tr//td//div//div//div//div//div/@class')]
    sides = [sides[x:x + 2] for x in range(0, len(sides), 2)]
    links = tree.xpath('//table[1]//tr//td[2]/a/@href')
    result["wars"] = [{"link": link, "attacker": attacker, "defender": defender} for link, (attacker, defender) in
                      zip(links, sides)]
    naps = tree.xpath('//table[2]//tr//td/b/text()')
    naps_expires = [x.strip() for x in tree.xpath('//table[2]//tr//td[2]/text()')][1:]
    result["naps"] = [{"country": naps, "expires": naps_expires} for naps, naps_expires in zip(naps, naps_expires)]
    allies = tree.xpath('//table[3]//tr//td/b/text()')
    expires = [x.strip() for x in tree.xpath('//table[3]//tr//td[2]/text()')][1:]
    result["mpps"] = [{"country": allies, "expires": expires} for allies, expires in zip(allies, expires)]
    return result


def newspaper(tree: fromstring) -> dict:
    titles = tree.xpath('//*[@id="esim-layout"]//table//tr//td//div[2]//a[1]/text()')
    article_ids = [int(x.split("?id=")[1]) for x in
                   tree.xpath('//*[@id="esim-layout"]//table//tr//td//div[2]//a[1]/@href')]
    posted_list = [x.replace("Posted ", "").strip() for x in
                   tree.xpath('//*[@id="esim-layout"]//table//tr//td//div[2]/text()') if x.strip()]
    votes = [int(x) for x in tree.xpath('//*[@id="esim-layout"]//table//tr//td//div[1]/text()')]
    last_page = tree.xpath("//ul[@id='pagination-digg']//li[last()-1]//@href") or ['page=1']
    last_page = int(last_page[0].split('page=')[1])
    subs = int(tree.xpath('//*[@id="mobileNewspaperStatusContainer"]//div[3]//div/text()')[0].strip())
    redactor = tree.xpath('//*[@id="mobileNewspaperStatusContainer"]/div[1]/a/text()')[0].strip()
    redactor_id = int(get_ids_from_path(tree, '//*[@id="mobileNewspaperStatusContainer"]/div[1]//a')[0])
    result = {"subs": subs, "pages": last_page, "redactor": redactor, "redactor_id": redactor_id,
              "articles": [{"title": title, "id": article_id, "posted": posted, "votes": votes} for
                           title, article_id, posted, votes in zip(
                      titles, article_ids, posted_list, votes)]}
    return result


def party(tree: fromstring) -> dict:
    name = tree.xpath('//*[@id="unitStatusHead"]//div/a/text()')[0]
    country = tree.xpath('//*[@class="countryNameTranslated"]/text()')[0]
    result = {"members_list": [], "country": country, "name": name}

    for x in tree.xpath('//*[@class="muColEl"]/b/text()'):
        x = x.split(":")
        if len(x) == 2:
            x[1] = x[1].replace(",", "").strip()
            if x[1]:
                result[x[0].replace(" ", "_").lower()] = int(x[1]) if x[1].isdigit() else x[1]

    nicks = tree.xpath('//*[@id="mobilePartyMembersWrapper"]//div[1]/a/text()')
    member_ids = [int(x.split("?id=")[1]) for x in tree.xpath('//*[@id="mobilePartyMembersWrapper"]//div[1]/a/@href')]
    joined = tree.xpath('//*[@id="mobilePartyMembersWrapper"]//div[2]/i/text()')
    for index, (nick, member_id, joined) in enumerate(zip(nicks, member_ids, joined)):
        icons = tree.xpath(f'//*[@id="mobilePartyMembersWrapper"][{index + 1}]//div[1]//i/@title')
        if icons and "Party Leader" in icons[0]:
            icons[0] = icons[0].replace("Party Leader", "")
            icons.insert(0, "Party Leader")
        result["members_list"].append({"nick": nick.strip(), "id": member_id, "joined": joined, "roles": icons})
    return result


def productMarket(tree: fromstring) -> dict:
    last_page = tree.xpath("//ul[@id='pagination-digg']//li[last()-1]//@href") or ['page=1']
    last_page = int(last_page[0].split('page=')[1])

    raw_products = tree.xpath("//*[@class='productMarketOfferList']//*[@class='product']//div//img/@src") or \
                   tree.xpath("//*[@id='productMarketItems']//*[@class='product']//div//img/@src")
    products = []
    i = -1
    for product in raw_products:
        product = product.replace("_", " ").split("/")[-1].split(".png")[0]
        if product.startswith("q") and len(product) == 2:
            products[i] = product.upper() + " " + products[i]
        else:
            products.append(product)
            i += 1

    seller_ids = [x.split("=")[-1] for x in tree.xpath("//*[@class='offerer']//@href")]
    sellers = tree.xpath("//*[@class='offerer']//a/text()")
    raw_prices = [float(x) for x in tree.xpath("//tr[position()>1]//td[4]/b/text()")][::2]
    ccs = [x.strip() for x in tree.xpath("//tr[position()>1]//td[4]/text()") if x.strip()][::2]
    stocks = tree.xpath("//tr[position()>1]//td[3]/text()")
    if not raw_prices:  # temp, new style in some servers.
        raw_prices = tree.xpath("//*[@class='productMarketOffer']//b/text()")[::2]
        ccs = [x.strip() for x in tree.xpath("//*[@class='price']/div/text()") if x.strip()][::3]
        stocks = tree.xpath("//*[@class='quantity']/text()")
    result = {"pages": last_page, "offers": []}
    for seller_id, seller, product, cc, price, stock in zip(
            seller_ids, sellers, products, ccs, raw_prices, stocks):
        result["offers"].append(
            {"seller": seller.strip(), "seller_id": int(seller_id), "product": product, "coin": cc, "price": price,
             "stock": int(stock.strip())})
    return result


def battlesByWar(tree: fromstring) -> dict:
    last_page = tree.xpath("//ul[@id='pagination-digg']//li[last()-1]//@href") or ['page=1']
    last_page = int(last_page[0].split('page=')[1])
    war = tree.xpath('//*[@name="id"]//option[@selected="selected"]')[0].text.strip()

    sides = [x.replace("xflagsMedium xflagsMedium-", "").replace("-", " ") for x in
             tree.xpath('//*[@id="battlesTable"]//tr//td[1]//div//div//div/@class') if "xflagsMedium" in x]
    defender, attacker = sides[::2], sides[1::2]
    battles_id = [int(x.split("?id=")[1]) for x in tree.xpath('//tr//td[1]//div//div[2]//div[2]/a/@href')]
    battles_region = tree.xpath('//tr//td[1]//div//div[2]//div[2]/a/text()')

    score = tree.xpath('//tr[position()>1]//td[2]/text()')
    dmg = [int(x.replace(",", "").strip()) for x in tree.xpath('//tr[position()>1]//td[3]/text()')]
    battle_start = [x.strip() for x in tree.xpath('//tr[position()>1]//td[4]/text()')]
    result = {"pages": last_page, "war": war, "battles": []}
    for defender, attacker, battle_id, battle_region, score, dmg, battle_start in zip(
            defender, attacker, battles_id, battles_region, score, dmg, battle_start):
        result["battles"].append({"defender_name": defender, "defender_score": int(score.strip().split(":")[0]),
                                  "attacker_name": attacker, "attacker_score": int(score.strip().split(":")[1]),
                                  "battle_id": battle_id, "dmg": dmg, "region": battle_region,
                                  "battle_start": battle_start})
    return result


def battles(tree: fromstring) -> dict:
    last_page = tree.xpath("//ul[@id='pagination-digg']//li[last()-1]//@href") or ['page=1']
    last_page = int(last_page[0].split('page=')[1])
    country = tree.xpath('//*[@id="countryId"]//option[@selected="selected"]')[0].text
    country_id = int(tree.xpath('//*[@id="countryId"]//option[@selected="selected"]/@value')[0])
    sorting = tree.xpath('//*[@id="sorting"]//option[@selected="selected"]')[0].text.replace("Sort ", "")
    filtering = tree.xpath('//*[@id="filter"]//option[@selected="selected"]')[0].text

    total_dmg = tree.xpath('//*[@class="battleTotalDamage"]/text()')
    progress_attackers = [float(x.replace("%", "")) for x in tree.xpath('//*[@id="attackerScoreInPercent"]/text()')]
    attackers_dmg = tree.xpath('//*[@id="attackerDamage"]/text()')
    defenders_dmg = tree.xpath('//*[@id="defenderDamage"]/text()')
    counters = [i.split(");\n")[0] for i in tree.xpath('//*[@id="battlesTable"]//div//div//script/text()') for i in
                i.split("() + ")[1:]]
    counters = [f'{int(x[0]):02d}:{int(x[1]):02d}:{int(x[2]):02d}' for x in chunker(counters, 3)]
    sides = tree.xpath('//*[@class="battleHeader"]//em/text()')
    battle_ids = tree.xpath('//*[@class="battleHeader"]//a/@href')
    battle_regions = tree.xpath('//*[@class="battleHeader"]//a/text()')
    scores = tree.xpath('//*[@class="battleFooterScore hoverText"]/text()')
    result = {"pages": last_page, "sorting": sorting, "filter": filtering, "country": country, "country_id": country_id,
              "battles": []}
    for i, (dmg, progress_attacker, counter, sides, battle_id, battle_region, score) in enumerate(zip(
            total_dmg, progress_attackers, counters, sides, battle_ids, battle_regions, scores)):
        defender, attacker = sides.split(" vs ")
        result["battles"].append(
            {"total_dmg": dmg, "time_reminding": counter, "battle_id": int(battle_id.split("=")[-1]),
             "region": battle_region,
             "defender": {"name": defender, "score": int(score.strip().split(":")[0]),
                          "bar": round(100 - progress_attacker, 2)},
             "attacker": {"name": attacker, "score": int(score.strip().split(":")[1]),
                          "bar": progress_attacker}})
        if attackers_dmg:
            try:
                result["battles"][-1]["defender"]["dmg"] = int(defenders_dmg[i].replace(",", ""))
                result["battles"][-1]["attacker"]["dmg"] = int(attackers_dmg[i].replace(",", ""))
            except:
                pass
    return result


def profile(tree: fromstring) -> dict:
    all_parameters = ["avoid", "max", "crit", "damage", "dmg", "miss", "flight", "consume", "eco", "str", "hit",
                      "less", "find", "split", "production", "merging", "restore", "increase"]
    medals_headers = ["congress", "cp", "train", "inviter", "subs", "work", "bh", "rw", "tester", "tournament"]
    friends = ([x.replace("Friends", "").replace("(", "").replace(")", "") for x in
                tree.xpath("//div[@class='rank']/text()") if "Friends" in x] or [0])[0]
    inactive = [int(x.split()[-2]) for x in tree.xpath('//*[@class="profile-data red"]/text()') if
                "This citizen has been inactive for" in x]
    status = "" if not inactive else str(date.today() - timedelta(days=inactive[0]))
    banned_by = [x.strip() for x in tree.xpath('//*[@class="profile-data red"]//div/a/text()')] or [""]
    premium = len(tree.xpath('//*[@class="premium-account"]')) != 0
    birthday = (tree.xpath('//*[@class="profile-result" and span = "Birthday"]/span/text()') or [1])[0]
    debts = sum(float(x) for x in tree.xpath('//*[@class="profile-data red"]//li/text()')[::6])
    assets = sum(float(x.strip()) for x in tree.xpath(
        '//*[@class="profile-data" and (strong = "Assets")]//ul//li/text()') if "\n" in x)
    is_online = tree.xpath('//*[@id="loginBar"]/div/span[2]/@class')[0] == "online"

    medals = {}
    for i, medal in enumerate(medals_headers, 1):
        medalse_count = tree.xpath(f"//*[@id='medals']//ul//li[{i}]//div//text()")
        if medalse_count:
            medals[medal.lower()] = int(medalse_count[0].replace("x", ""))
        elif "emptyMedal" not in tree.xpath(f"//*[@id='medals']//ul//li[{i}]/img/@src")[0]:
            medals[medal.lower()] = 1
        else:
            medals[medal.lower()] = 0

    buffs_debuffs = [
        camel_case_merge(x.split("/specialItems/")[-1].split(".png")[0]).replace("Elixir", "") for x in
        tree.xpath('//*[@class="profile-row" and (strong="Debuffs" or strong="Buffs")]//img/@src') if
        "//cdn.e-sim.org//img/specialItems/" in x]
    buffs = [x.split("_")[0].replace("Vacations", "Vac").replace("Resistance", "Sewer").replace(
        "Pain Dealer", "PD ").replace("Bonus Damage", "").replace("  ", " ") + (
                 "% Bonus" if "Bonus Damage" in x.split("_")[0] else "")
             for x in buffs_debuffs if "Positive" in x.split("_")[1:]]
    debuffs = [x.split("_")[0].lower().replace("Vacation", "Vac").replace(
        "Resistance", "Sewer").replace("  ", " ") for x in buffs_debuffs if "Negative" in x.split("_")[1:]]

    equipments = []
    for slot_path in tree.xpath('//*[@id="profileEquipmentNew"]//div//div//div//@title'):
        tree = fromstring(slot_path)
        try:
            eq_type = tree.xpath('//b/text()')[0].strip()
        except IndexError:
            continue

        parameters_string = tree.xpath('//p/text()')
        parameters = []
        values = []
        for parameter_string in parameters_string:
            for x in all_parameters:
                if x in parameter_string.lower():
                    parameters.append(x)
                    values.append(float(parameter_string.split(" ")[-1].replace("%", "").strip()))
                    break

        equipments.append(
            {"type": " ".join(eq_type.split()[1:]), "quality": eq_type.split()[0][1], "first_parameter": parameters[0],
             "second_parameter": parameters[1], "third_parameter": parameters[2] if len(parameters) == 3 else "",
             "first_value": values[0], "second_value": values[1], "third_value": values[2] if len(values) == 3 else 0})
    result = {"medals": medals, "friends": int(friends), "equipments": equipments,
              "inactive_days": inactive[0] if inactive else 0,
              "premium": premium, "birthday": birthday, "is_online": is_online,
              "assets": assets, "debts": debts, "buffs": buffs, "debuffs": debuffs}
    if banned_by and banned_by[0]:
        result.update({"banned_by": banned_by[0]})
    if status:
        result.update({"last_login": status})
    return result
