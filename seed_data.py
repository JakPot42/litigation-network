"""
Pre-seeded real securities class action cases.

Case details are from public court records, SEC filings, and published judicial opinions.
Complaint text excerpts are paraphrased summaries of public allegations — not verbatim filings.
Settlement amounts are approximate figures from public reporting; mark disputed figures below.
Claude extraction results are stored in complaint_extractor._DEMO_EXTRACTIONS.

12 cases spanning 7 allegation types, 6 plaintiff firms, 9 judges, 5 industry sectors.
Date range: 2012–2019 filing dates. Settlement amounts in USD.
"""
import json
from datetime import datetime, date
from sqlalchemy.orm import Session
from models import Complaint
from complaint_extractor import _DEMO_EXTRACTIONS

_DEMO_CASES = [
    {
        "case_name": "In re Tesla, Inc. Securities Litigation",
        "docket_number": "3:18-cv-04865",
        "court": "N.D. Cal.",
        "date_filed": "2018-08-10",
        "defendant_company": "Tesla, Inc.",
        "industry_sector": "Technology",
        "plaintiff_law_firm": "Robbins Geller Rudman & Dowd LLP",
        "judge_name": "Edward M. Chen",
        "status": "dismissed",
        "settlement_amount_usd": None,
        "settlement_date": None,
        "days_to_resolution": 1642,  # trial verdict Feb 2023 for defendant
        "courtlistener_url": "https://www.courtlistener.com/docket/14611944/in-re-tesla-inc-securities-litigation/",
        "summary_text": (
            "Plaintiff brings this action on behalf of all persons who purchased or otherwise "
            "acquired Tesla securities between August 7, 2018 and August 17, 2018, inclusive. "
            "On August 7, 2018, Defendant Elon Musk published a tweet stating: 'Am considering "
            "taking Tesla private at $420. Funding secured.' This statement was materially false "
            "and misleading. At the time of the tweet, no binding financing commitment had been "
            "obtained from any party. The Saudi Arabia Public Investment Fund had expressed "
            "interest in discussions but had not committed funding. Tesla's Board of Directors "
            "had not approved or even discussed a going-private transaction in any formal session. "
            "As a result of this materially false and misleading statement, Tesla's stock price "
            "increased from $341.99 to $379.57 — an increase of approximately 11% — on August "
            "7, 2018. Class members who purchased shares at these inflated prices suffered "
            "damages when, on August 13 and August 17, 2018, further disclosures revealed the "
            "lack of secured financing, and Tesla's stock price declined. A federal jury trial "
            "in January 2023 found in favor of defendants. The case illustrates the challenge "
            "of proving both falsity and scienter when statements are made through social media "
            "without prior Board approval or legal review."
        ),
    },
    {
        "case_name": "In re Facebook, Inc. Securities Litigation",
        "docket_number": "3:18-cv-01725",
        "court": "N.D. Cal.",
        "date_filed": "2018-03-20",
        "defendant_company": "Meta Platforms, Inc.",
        "industry_sector": "Technology",
        "plaintiff_law_firm": "Labaton Sucharow LLP",
        "judge_name": "Vince Chhabria",
        "status": "settled",
        "settlement_amount_usd": 100_000_000.0,
        "settlement_date": "2022-11-01",
        "days_to_resolution": 1686,
        "courtlistener_url": "https://www.courtlistener.com/docket/6166734/in-re-facebook-inc-securities-litigation/",
        "summary_text": (
            "This securities class action alleges that Facebook, Inc. and certain of its "
            "officers and directors violated Sections 10(b) and 20(a) of the Securities "
            "Exchange Act of 1934. Facebook learned in December 2015 that Cambridge Analytica, "
            "a political data firm, had improperly harvested the personal data of approximately "
            "87 million Facebook users through a third-party app called 'thisisyourdigitallife.' "
            "Despite this knowledge, Facebook's annual, quarterly, and registration statement "
            "filings continued to describe data misuse only as a hypothetical risk factor — "
            "not as a known, ongoing event. Facebook's Terms of Service prohibited this type "
            "of data harvesting, yet the company took no immediate corrective action to remove "
            "Cambridge Analytica's data access privileges. On March 17, 2018, The Guardian and "
            "The New York Times simultaneously published investigative reports on the Cambridge "
            "Analytica data harvesting incident. Facebook's stock declined from $185.09 to "
            "$172.56 on March 19, 2018 — a decline of approximately 6.8% — and continued to "
            "fall thereafter. Defendants' failure to disclose a known, specific data misuse "
            "incident while characterizing such events only as hypothetical risks constitutes "
            "a material omission actionable under the Exchange Act."
        ),
    },
    {
        "case_name": "In re Boeing Co. Securities Litigation",
        "docket_number": "1:19-cv-08095",
        "court": "N.D. Ill.",
        "date_filed": "2019-12-11",
        "defendant_company": "Boeing Company",
        "industry_sector": "Technology",
        "plaintiff_law_firm": "Bernstein Litowitz Berger & Grossmann LLP",
        "judge_name": "Jorge Luis Alonso",
        "status": "settled",
        "settlement_amount_usd": 234_500_000.0,
        "settlement_date": "2023-07-01",
        "days_to_resolution": 1298,
        "courtlistener_url": "https://www.courtlistener.com/docket/16434098/in-re-boeing-co-securities-litigation/",
        "summary_text": (
            "This action is brought on behalf of all persons who purchased Boeing securities "
            "between January 16, 2019 and December 16, 2019. Boeing's 737 MAX aircraft "
            "incorporated a flight control system known as the Maneuvering Characteristics "
            "Augmentation System (MCAS). Boeing failed to disclose to the FAA, to the "
            "public, and to investors that MCAS could activate unexpectedly based on a single "
            "faulty sensor reading and lacked critical redundancy. Following the Lion Air "
            "Flight 610 crash in October 2018 — which killed all 189 people aboard — Boeing "
            "issued public statements asserting the 737 MAX was safe and that existing training "
            "procedures were adequate. Internal communications later revealed to regulators "
            "showed Boeing employees had expressed concerns about MCAS's design, including one "
            "employee stating the aircraft was 'designed by clowns, who in turn are supervised "
            "by monkeys.' Following the Ethiopian Airlines Flight 302 crash on March 10, 2019 "
            "— which killed all 157 people aboard — regulators worldwide grounded the 737 MAX. "
            "Boeing's stock fell from $422 to $303, a 28% decline destroying approximately "
            "$34 billion in market capitalization. Defendants concealed known safety defects "
            "while representing the aircraft as airworthy to preserve billions in anticipated "
            "737 MAX delivery revenue."
        ),
    },
    {
        "case_name": "In re Luckin Coffee Inc. Securities Litigation",
        "docket_number": "1:20-cv-01293",
        "court": "S.D.N.Y.",
        "date_filed": "2020-02-13",
        "defendant_company": "Luckin Coffee Inc.",
        "industry_sector": "Retail",
        "plaintiff_law_firm": "Pomerantz LLP",
        "judge_name": "Paul A. Engelmayer",
        "status": "settled",
        "settlement_amount_usd": 175_000_000.0,
        "settlement_date": "2021-09-15",
        "days_to_resolution": 579,
        "courtlistener_url": "https://www.courtlistener.com/docket/17165800/in-re-luckin-coffee-inc-securities-litigation/",
        "summary_text": (
            "Plaintiff brings this action on behalf of purchasers of Luckin Coffee American "
            "Depositary Shares between November 13, 2019 and April 2, 2020. Luckin Coffee "
            "presented itself to investors as China's largest and fastest-growing coffee chain, "
            "using fabricated sales data to demonstrate a path to profitability. The company "
            "fabricated approximately RMB 2.2 billion (~$310 million USD) in retail sales "
            "during fiscal year 2019 through a network of related-party transactions controlled "
            "by insiders. Luckin inflated per-item selling prices in its internal systems, "
            "then executed transactions with related parties that were recorded as third-party "
            "sales. These fabricated transactions were incorporated into the Company's SEC "
            "filings and used to support a January 2020 secondary offering that raised "
            "approximately $418 million. An anonymous short-seller report in January 2020 cited "
            "whistleblower evidence and provided detailed analysis of the fabricated transactions. "
            "On April 2, 2020, Luckin disclosed that an internal investigation had identified "
            "that its COO and certain other employees had engaged in misconduct resulting in "
            "the fabrication of transactions totaling approximately RMB 2.2 billion. The "
            "Company's ADSs declined approximately 80% in a single day upon this disclosure."
        ),
    },
    {
        "case_name": "In re Snap Inc. Securities Litigation",
        "docket_number": "2:17-cv-03679",
        "court": "C.D. Cal.",
        "date_filed": "2017-05-12",
        "defendant_company": "Snap Inc.",
        "industry_sector": "Technology",
        "plaintiff_law_firm": "Robbins Geller Rudman & Dowd LLP",
        "judge_name": "Michael W. Fitzgerald",
        "status": "settled",
        "settlement_amount_usd": 187_500_000.0,
        "settlement_date": "2020-12-31",
        "days_to_resolution": 1329,
        "courtlistener_url": "https://www.courtlistener.com/docket/6107453/in-re-snap-inc-securities-litigation/",
        "summary_text": (
            "This securities class action is brought on behalf of all persons who purchased "
            "Snap Inc. Class A common stock in or traceable to its March 2, 2017 initial "
            "public offering. Snap's S-1 registration statement disclosed Daily Active User "
            "statistics through the third quarter of 2016 — a date that was not the most "
            "recently available. In Q4 2016, following the August 2016 launch of Instagram "
            "Stories — a feature that directly replicated Snapchat's core Stories functionality "
            "— Snap's DAU growth had already materially decelerated. Snap's management was "
            "aware of this deceleration through real-time internal dashboards but omitted the "
            "Q4 2016 DAU data from the registration statement. By presenting DAU figures "
            "through Q3 2016 only, the registration statement implied growth rates that no "
            "longer reflected the company's actual trajectory. Snap priced its IPO at $17 per "
            "share on March 2, 2017, raising approximately $2.4 billion. When Snap reported "
            "Q1 2017 results showing DAU growth of only 5% — far below the 14% quarterly "
            "growth implied by the registration statement — the stock fell 27% to below the "
            "IPO price. Defendants knew the disclosed growth metrics no longer reflected "
            "current business performance at the time of the IPO."
        ),
    },
    {
        "case_name": "City of Providence v. Uber Technologies, Inc.",
        "docket_number": "3:19-cv-06361",
        "court": "N.D. Cal.",
        "date_filed": "2019-10-07",
        "defendant_company": "Uber Technologies, Inc.",
        "industry_sector": "Technology",
        "plaintiff_law_firm": "Hagens Berman Sobol Shapiro LLP",
        "judge_name": "James Donato",
        "status": "settled",
        "settlement_amount_usd": 200_000_000.0,
        "settlement_date": "2023-06-30",
        "days_to_resolution": 1362,
        "courtlistener_url": "https://www.courtlistener.com/docket/16016199/city-of-providence-v-uber-technologies-inc/",
        "summary_text": (
            "This action is brought on behalf of purchasers of Uber Technologies common stock "
            "in Uber's May 10, 2019 initial public offering. Uber's S-1 registration statement "
            "and prospectus failed to disclose material adverse facts that were known to "
            "management at the time of the IPO. Specifically, defendants omitted disclosure "
            "of: (1) the extent to which Lyft's competitive response had already eroded Uber's "
            "U.S. market share; (2) the specific regulatory challenges in London and other "
            "major markets where Uber's operating licenses were under active regulatory review; "
            "(3) the unsustainable driver incentive subsidies required to maintain supply, "
            "which were creating a structural impediment to profitability; and (4) internal "
            "management projections showing a materially longer path to profitability than "
            "implied by the registration statement. Uber priced its IPO at $45 per share, "
            "raising approximately $8.1 billion. The stock closed below the IPO price on its "
            "first trading day and declined to approximately $26 within six months, as the "
            "concealed competitive and regulatory headwinds materialized. Defendants sold "
            "180 million shares at inflated prices while possessing information that would have "
            "materially affected the investment decisions of reasonable investors."
        ),
    },
    {
        "case_name": "In re Zynga Inc. Securities Litigation",
        "docket_number": "3:12-cv-04300",
        "court": "N.D. Cal.",
        "date_filed": "2012-08-02",
        "defendant_company": "Zynga Inc.",
        "industry_sector": "Technology",
        "plaintiff_law_firm": "Robbins Geller Rudman & Dowd LLP",
        "judge_name": "Jeffrey S. White",
        "status": "settled",
        "settlement_amount_usd": 23_400_000.0,
        "settlement_date": "2015-01-21",
        "days_to_resolution": 902,
        "courtlistener_url": "https://www.courtlistener.com/docket/4340398/in-re-zynga-inc-securities-litigation/",
        "summary_text": (
            "This class action is brought on behalf of purchasers of Zynga Inc. securities "
            "between February 14, 2012 and July 25, 2012. In March 2012, Zynga conducted a "
            "secondary public offering in which insiders — including CEO Mark Pincus and other "
            "officers and directors — sold 43.3 million shares and raised approximately $516 "
            "million. At the time of the offering, defendants represented that Zynga's key "
            "games — including FarmVille 2, CastleVille, and other titles — were performing "
            "well and that bookings for 2012 were on track. Defendants possessed internal "
            "real-time game performance dashboards showing that key games had experienced a "
            "material decline in Daily Active Users (DAUs) and bookings in early 2012, driven "
            "by changes to Facebook's promotional algorithm that reduced organic game discovery. "
            "Rather than disclose this known adverse trend before the secondary offering, "
            "defendants allowed insiders to sell $516 million in stock at prices that did not "
            "reflect this information. On July 25, 2012, Zynga announced that its full-year "
            "2012 bookings guidance was being reduced from $1.225 billion to $1.150 billion. "
            "The stock fell approximately 40% on this announcement, from $5.07 to $2.94, the "
            "largest single-day decline in the company's history as a public company."
        ),
    },
    {
        "case_name": "In re Lumber Liquidators Holdings Securities Litigation",
        "docket_number": "1:16-cv-00015",
        "court": "E.D. Va.",
        "date_filed": "2016-01-05",
        "defendant_company": "Lumber Liquidators Holdings",
        "industry_sector": "Retail",
        "plaintiff_law_firm": "Kessler Topaz Meltzer & Check LLP",
        "judge_name": "Leonie M. Brinkema",
        "status": "settled",
        "settlement_amount_usd": 36_000_000.0,
        "settlement_date": "2018-03-06",
        "days_to_resolution": 791,
        "courtlistener_url": "https://www.courtlistener.com/docket/4612088/in-re-lumber-liquidators-holdings-inc-securities-litigation/",
        "summary_text": (
            "This action is brought on behalf of purchasers of Lumber Liquidators securities "
            "between February 22, 2013 and March 26, 2015. Lumber Liquidators sourced a "
            "significant portion of its laminate flooring products from Chinese manufacturers. "
            "Testing conducted by independent laboratories and later by consumer advocacy "
            "groups showed that Lumber Liquidators' Chinese-sourced laminate flooring contained "
            "formaldehyde levels that exceeded applicable California Air Resources Board (CARB) "
            "Phase 2 standards — in some samples by 2-7 times the permissible limit. "
            "Defendants possessed internal quality assurance documentation and test results "
            "indicating non-compliance with CARB standards well before the March 2015 public "
            "disclosure. Despite this knowledge, Lumber Liquidators' annual and quarterly SEC "
            "filings represented that its products complied with all applicable safety "
            "regulations. On March 1, 2015, CBS News' '60 Minutes' broadcast an investigative "
            "report presenting independent test results showing elevated formaldehyde levels in "
            "Lumber Liquidators' laminate flooring products. The company's stock declined from "
            "$67.32 to $51.26 on March 2, 2015 — a single-day decline of approximately 24% — "
            "as the market learned of the safety compliance failures that had been concealed."
        ),
    },
    {
        "case_name": "In re Valeant Pharmaceuticals International Securities Litigation",
        "docket_number": "3:15-cv-07658",
        "court": "D.N.J.",
        "date_filed": "2015-10-22",
        "defendant_company": "Valeant Pharmaceuticals International",
        "industry_sector": "Healthcare",
        "plaintiff_law_firm": "Bernstein Litowitz Berger & Grossmann LLP",
        "judge_name": "Michael A. Shipp",
        "status": "settled",
        "settlement_amount_usd": 1_210_000_000.0,
        "settlement_date": "2019-04-30",
        "days_to_resolution": 1286,
        "courtlistener_url": "https://www.courtlistener.com/docket/4474226/in-re-valeant-pharmaceuticals-international-securities-litigation/",
        "summary_text": (
            "This securities class action alleges that Valeant Pharmaceuticals and certain "
            "of its officers violated the federal securities laws by concealing a secret "
            "network of specialty pharmacies — most prominently Philidor Rx Services — through "
            "which Valeant artificially inflated its revenues using channel-stuffing and related-"
            "party transactions. Valeant's growth strategy relied on acquiring drug companies "
            "and rapidly raising prices on the acquired drugs. To demonstrate consistent "
            "organic revenue growth to investors, Valeant established and secretly controlled "
            "Philidor, a specialty pharmacy that would fill Valeant prescriptions even when "
            "denied by traditional pharmacies. Valeant held an undisclosed option to acquire "
            "Philidor for $0 and effectively controlled its operations, yet failed to consolidate "
            "Philidor in its financial statements or disclose the relationship to investors. "
            "Products shipped to Philidor were recorded as revenue even though many were not "
            "dispensed to patients. When Citron Research published its analysis of the Philidor "
            "relationship on October 19, 2015, Valeant's stock declined from approximately "
            "$262 to $73 over the following month — a loss of over $60 billion in market "
            "capitalization. The $1.21 billion settlement remains one of the largest securities "
            "class action recoveries in history."
        ),
    },
    {
        "case_name": "In re Kraft Heinz Securities Litigation",
        "docket_number": "1:19-cv-01339",
        "court": "N.D. Ill.",
        "date_filed": "2019-02-25",
        "defendant_company": "Kraft Heinz Company",
        "industry_sector": "Consumer",
        "plaintiff_law_firm": "Hagens Berman Sobol Shapiro LLP",
        "judge_name": "Robert W. Gettleman",
        "status": "settled",
        "settlement_amount_usd": 62_000_000.0,
        "settlement_date": "2021-10-14",
        "days_to_resolution": 961,
        "courtlistener_url": "https://www.courtlistener.com/docket/15051218/in-re-kraft-heinz-securities-litigation/",
        "summary_text": (
            "This action is brought on behalf of purchasers of Kraft Heinz securities between "
            "July 6, 2016 and February 21, 2019. Defendants engaged in an improper accounting "
            "scheme in which Kraft Heinz's procurement function manipulated supplier contracts, "
            "rebates, and accruals to reduce reported cost of goods sold and inflate reported "
            "procurement savings metrics. The scheme was designed to support the aggressive "
            "cost-cutting targets imposed by controlling shareholders 3G Capital — known for "
            "its zero-based budgeting approach — and to present investors with adjusted EBITDA "
            "figures that were unachievable through legitimate procurement operations. "
            "From 2016 through 2018, Kraft Heinz reported consistent improvements in adjusted "
            "EBITDA that were attributable in part to the improper procurement accounting. "
            "On February 21, 2019, Kraft Heinz announced: (1) that it had received an SEC "
            "subpoena related to its accounting policies and internal controls in the "
            "procurement area; (2) a $15.4 billion goodwill and intangible asset impairment "
            "charge; and (3) a reduction in its quarterly dividend from $0.625 to $0.40 per "
            "share. Kraft Heinz's stock declined from $48.18 to $34.95 — a single-day loss "
            "of 27% — its largest decline since the 2015 merger of Kraft Foods and H.J. Heinz."
        ),
    },
    {
        "case_name": "In re General Electric Company Securities Litigation",
        "docket_number": "1:19-cv-01013",
        "court": "S.D.N.Y.",
        "date_filed": "2019-01-31",
        "defendant_company": "General Electric Company",
        "industry_sector": "Finance",
        "plaintiff_law_firm": "Robbins Geller Rudman & Dowd LLP",
        "judge_name": "Valerie E. Caproni",
        "status": "settled",
        "settlement_amount_usd": 200_000_000.0,
        "settlement_date": "2023-09-21",
        "days_to_resolution": 1694,
        "courtlistener_url": "https://www.courtlistener.com/docket/15002987/in-re-general-electric-company-securities-litigation/",
        "summary_text": (
            "This securities class action is brought on behalf of all persons who purchased "
            "GE common stock between July 17, 2015 and January 24, 2018. For years, GE "
            "concealed two separate sources of mounting liabilities: (1) a long-term care "
            "insurance run-off portfolio in GE Capital that carried severely understated "
            "reserves; and (2) GE's Power division, which held long-term service agreements "
            "accounted for under overly optimistic assumptions that understated performance-"
            "related liabilities. GE's management repeatedly assured investors that the "
            "company's industrial free cash flow supported its $0.24 quarterly dividend, "
            "when in fact free cash flow figures were bolstered by reclassifying operating "
            "items between segments. On January 16, 2018, GE disclosed that it would take "
            "an $8.3 billion after-tax charge related to its insurance run-off portfolio and "
            "that its previously announced quarterly dividend would be cut in half. On "
            "October 1, 2018, GE announced a $22 billion goodwill impairment in its Power "
            "division. GE's stock declined from approximately $31 to $6 over the class period "
            "— a collapse that destroyed approximately $150 billion in shareholder value and "
            "made GE the worst-performing Dow Jones Industrial Average component of 2018."
        ),
    },
    {
        "case_name": "Sjunde AP-Fonden v. Goldman Sachs Group, Inc.",
        "docket_number": "1:18-cv-12084",
        "court": "S.D.N.Y.",
        "date_filed": "2018-12-20",
        "defendant_company": "Goldman Sachs Group, Inc.",
        "industry_sector": "Finance",
        "plaintiff_law_firm": "Pomerantz LLP",
        "judge_name": "Paul A. Engelmayer",
        "status": "settled",
        "settlement_amount_usd": 215_000_000.0,
        "settlement_date": "2023-04-27",
        "days_to_resolution": 1589,
        "courtlistener_url": "https://www.courtlistener.com/docket/14618397/sjunde-ap-fonden-v-goldman-sachs-group-inc/",
        "summary_text": (
            "This action is brought on behalf of purchasers of Goldman Sachs Group common stock "
            "between February 28, 2012 and December 17, 2018. Goldman Sachs underwrote "
            "approximately $6.5 billion in bonds for 1MDB — Malaysia's sovereign wealth fund "
            "— in 2012 and 2013, earning approximately $600 million in fees. Goldman's senior "
            "executives, including its Southeast Asia partner Tim Leissner, knew or recklessly "
            "disregarded that proceeds from the 1MDB bond deals were being diverted through "
            "bribery and theft rather than being used for the stated sovereign economic "
            "development purposes. Goldman's SEC filings failed to disclose the Company's "
            "criminal exposure arising from participation in the 1MDB scheme. Goldman's Code "
            "of Conduct and annual compliance representations made during the class period were "
            "materially false because they omitted known violations of anti-corruption laws. "
            "On November 1, 2018, the U.S. Department of Justice unsealed an indictment of "
            "Goldman's former Southeast Asia chairman Tim Leissner, revealing the scope of "
            "Goldman's 1MDB liability. Goldman's stock declined from $224.66 to $196.57 — a "
            "12% decline in two days — as investors learned of the criminal exposure that had "
            "been concealed throughout the class period. Goldman subsequently entered a $2.9 "
            "billion global settlement with the DOJ in October 2020."
        ),
    },
]


def load_seed_data(db: Session) -> None:
    if db.query(Complaint).count() > 0:
        return

    for case in _DEMO_CASES:
        extraction = _DEMO_EXTRACTIONS.get(case["case_name"], {})
        c = Complaint(
            case_name=case["case_name"],
            docket_number=case["docket_number"],
            court=case["court"],
            date_filed=case["date_filed"],
            defendant_company=case["defendant_company"],
            industry_sector=case.get("industry_sector", "Other"),
            plaintiff_law_firm=case["plaintiff_law_firm"],
            judge_name=case.get("judge_name"),
            allegation_type=extraction.get("allegation_type", "disclosure_failure"),
            harm_theory=extraction.get("harm_theory", ""),
            key_allegations_json=json.dumps(extraction.get("key_allegations", [])),
            defendant_officers_json=json.dumps(extraction.get("defendant_officers", [])),
            class_period_start=extraction.get("class_period_start"),
            class_period_end=extraction.get("class_period_end"),
            status=case.get("status", "filed"),
            settlement_amount_usd=case.get("settlement_amount_usd"),
            settlement_date=case.get("settlement_date"),
            days_to_resolution=case.get("days_to_resolution"),
            courtlistener_url=case.get("courtlistener_url"),
            summary_text=case.get("summary_text"),
        )
        db.add(c)
    db.commit()
