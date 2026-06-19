"""
Extracts allegation type and harm theory from securities complaint text using Claude.

Claude's job: read complaint text → identify what category of fraud is alleged →
articulate HOW investors were harmed. This is genuine document-level extraction,
not metadata lookup or rule-based classification.

In DEMO_MODE, returns pre-baked results so the UI works on Render without API calls.
"""
import json
from config import DEMO_MODE, CLAUDE_MODEL, ANTHROPIC_API_KEY, ALLEGATION_TYPES

_SYSTEM_PROMPT = """You are a securities litigation analyst. Given an excerpt from a
securities class action complaint, extract structured information about the alleged fraud.

Return ONLY valid JSON with these fields:
- allegation_type: one of {types}
- harm_theory: 2-3 sentences describing exactly HOW the alleged misconduct caused
  investor harm (price inflation mechanism + corrective disclosure)
- key_allegations: list of 3-5 specific factual allegations from the complaint
- defendant_officers: list of named individual defendants (e.g. "CEO John Smith")
- class_period_start: YYYY-MM-DD or null
- class_period_end: YYYY-MM-DD or null
- industry_sector: one of Technology, Finance, Healthcare, Energy, Consumer, Retail, Other

No prose outside the JSON.""".format(types=json.dumps(ALLEGATION_TYPES))

# Pre-baked extractions for DEMO_MODE — what Claude would extract from each complaint text.
# Keyed by case_name.
_DEMO_EXTRACTIONS = {
    "In re Tesla, Inc. Securities Litigation": {
        "allegation_type": "disclosure_failure",
        "harm_theory": (
            "Defendants artificially inflated Tesla's stock price by making materially "
            "false and misleading statements regarding Elon Musk's August 7, 2018 tweet "
            "claiming 'funding secured' for a go-private transaction at $420 per share. "
            "Investors who purchased shares between August 7 and August 17, 2018 suffered "
            "damages when the SEC disclosed no binding funding had been arranged, causing "
            "the stock to decline from its inflated price."
        ),
        "key_allegations": [
            "Musk's 'funding secured' tweet was materially false — no binding financing commitment existed",
            "Musk and Tesla failed to correct the misimpression created by the public statement",
            "Class members purchased shares at prices artificially inflated by the misrepresentation",
            "The August 17 disclosure that financing was not certain caused the stock to decline sharply",
            "Tesla's board was aware the statement was premature before it was made public",
        ],
        "defendant_officers": ["CEO Elon Musk"],
        "class_period_start": "2018-08-07",
        "class_period_end": "2018-08-17",
        "industry_sector": "Technology",
    },
    "In re Facebook, Inc. Securities Litigation": {
        "allegation_type": "disclosure_failure",
        "harm_theory": (
            "Facebook failed to disclose that Cambridge Analytica had improperly obtained "
            "the personal data of up to 87 million users and that the company knew of the "
            "data misuse as early as 2015. This failure to disclose a known data security "
            "risk and regulatory exposure caused investors to purchase shares at inflated "
            "prices; when The Guardian and New York Times reported the data misuse in March "
            "2018, the stock declined approximately 9% in two days."
        ),
        "key_allegations": [
            "Facebook learned of Cambridge Analytica's data misuse in December 2015 but did not disclose it",
            "SEC risk factor disclosures omitted known, specific data misuse events as hypothetical risks",
            "Facebook's privacy settings allowed third-party apps to harvest friends' data without consent",
            "Defendants made repeated public assurances about data protection inconsistent with known facts",
            "When corrective disclosures emerged, the stock fell approximately $58 in two trading days",
        ],
        "defendant_officers": ["CEO Mark Zuckerberg", "COO Sheryl Sandberg", "CFO David Wehner"],
        "class_period_start": "2017-02-03",
        "class_period_end": "2018-03-19",
        "industry_sector": "Technology",
    },
    "In re Boeing Co. Securities Litigation": {
        "allegation_type": "disclosure_failure",
        "harm_theory": (
            "Boeing failed to disclose known safety defects in the 737 MAX's Maneuvering "
            "Characteristics Augmentation System (MCAS) while representing the aircraft as "
            "safe and FAA-certified. Following the Lion Air crash (October 2018) and "
            "Ethiopian Airlines crash (March 2019), the global grounding of the 737 MAX "
            "caused Boeing's stock to decline from $422 to $303, a 28% loss, wiping out "
            "tens of billions in market capitalization."
        ),
        "key_allegations": [
            "Boeing concealed MCAS design flaws from the FAA during the certification process",
            "Internal communications showed employees knew MCAS was 'designed by clowns' but changes were suppressed",
            "Boeing falsely represented to investors and regulators that the 737 MAX was airworthy",
            "The company pressured the FAA to approve the aircraft to avoid costly pilot retraining",
            "After Lion Air crash, Boeing failed to ground the fleet and continued to misrepresent safety",
        ],
        "defendant_officers": [
            "CEO Dennis Muilenburg",
            "CFO Gregory Smith",
            "Former CEO Jim McNerney",
        ],
        "class_period_start": "2019-01-16",
        "class_period_end": "2019-12-16",
        "industry_sector": "Technology",
    },
    "In re Luckin Coffee Inc. Securities Litigation": {
        "allegation_type": "accounting_fraud",
        "harm_theory": (
            "Luckin Coffee fabricated approximately RMB 2.2 billion (~$310 million) in "
            "retail sales through a network of undisclosed related-party transactions and "
            "inflated per-item pricing in internal systems. Investors who purchased shares "
            "in Luckin's January 2020 secondary offering at $33 per share suffered near-total "
            "losses when the company disclosed the fraud in April 2020, causing the stock to "
            "collapse by approximately 80% in a single day."
        ),
        "key_allegations": [
            "Luckin fabricated transactions totaling approximately RMB 2.2 billion in 2019",
            "Per-item selling prices were inflated in internal systems to boost reported revenue",
            "The Company used a network of related-party entities controlled by insiders to create sham sales",
            "Defendants used fraudulently inflated revenue figures to support a $418 million secondary offering",
            "An anonymous short-seller report in January 2020 cited internal whistleblower evidence of the fraud",
        ],
        "defendant_officers": [
            "Chairman Charles Lu Zhengyao",
            "CEO Jenny Qian Zhiya",
            "COO Jian Liu",
        ],
        "class_period_start": "2019-11-13",
        "class_period_end": "2020-04-02",
        "industry_sector": "Retail",
    },
    "In re Snap Inc. Securities Litigation": {
        "allegation_type": "forward_looking_statements",
        "harm_theory": (
            "Snap's March 2017 IPO registration statement omitted that the company had already "
            "experienced a severe decline in Daily Active User growth in Q4 2016 due to Instagram "
            "Stories, a directly competitive feature launched in August 2016. By presenting DAU "
            "growth figures only through Q3 2016, defendants sold shares at $17 while concealing "
            "a known trend of decelerating growth; when Q1 2017 results revealed DAU growth had "
            "fallen to 5%, the stock dropped 27% below the IPO price."
        ),
        "key_allegations": [
            "Snap's S-1 registration statement disclosed only DAU figures through Q3 2016, omitting Q4 2016 deceleration",
            "Instagram Stories launched August 2016 directly replicating Snapchat's core functionality",
            "Snap internally tracked the impact of Instagram Stories on DAU growth throughout late 2016",
            "The IPO prospectus presented historical growth rates that no longer reflected current trends",
            "Snap's Q1 2017 earnings revealed DAU growth of only 5%, far below the rates implied by the prospectus",
        ],
        "defendant_officers": ["CEO Evan Spiegel", "CTO Bobby Murphy", "CFO Andrew Vollero"],
        "class_period_start": "2017-03-02",
        "class_period_end": "2017-05-15",
        "industry_sector": "Technology",
    },
    "City of Providence v. Uber Technologies, Inc.": {
        "allegation_type": "disclosure_failure",
        "harm_theory": (
            "Uber's May 2019 IPO prospectus failed to disclose material adverse facts about "
            "the competitive landscape, regulatory risks, and driver economics that were known "
            "to management. Uber sold 180 million shares at $45 in the IPO; the stock declined "
            "below $30 within six months as the concealed competitive pressures and path to "
            "profitability concerns materialized, causing investors to suffer billions in losses."
        ),
        "key_allegations": [
            "Uber's S-1 failed to disclose specific cost pressures and competitive responses already underway",
            "The company overstated the Total Addressable Market and its ability to capture it profitably",
            "Known regulatory risks in key markets were described only in vague, generalized terms",
            "Driver supply constraints and rising driver incentive costs were omitted from risk disclosures",
            "Internal projections showed narrowing path to profitability that was not disclosed to IPO investors",
        ],
        "defendant_officers": ["CEO Dara Khosrowshahi", "CFO Nelson Chai"],
        "class_period_start": "2019-05-10",
        "class_period_end": "2019-11-06",
        "industry_sector": "Technology",
    },
    "In re Zynga Inc. Securities Litigation": {
        "allegation_type": "forward_looking_statements",
        "harm_theory": (
            "Zynga's officers made materially misleading statements about the company's "
            "bookings growth and user engagement metrics while insiders sold over $500 million "
            "in stock. Defendants concealed that Zynga's key games (FarmVille 2, CastleVille) "
            "were experiencing steep declines in DAU and bookings in mid-2012; when the company "
            "slashed its 2012 guidance in July 2012, the stock fell 40% in a single day."
        ),
        "key_allegations": [
            "Zynga executives sold $516 million in stock in a March 2012 secondary offering using insider knowledge",
            "The company made bullish Q2 and full-year 2012 guidance statements while internal data showed declining bookings",
            "DAU and MAU metrics for key games were declining due to Facebook platform algorithm changes",
            "Management possessed real-time game performance dashboards showing the deterioration",
            "The July 25, 2012 guidance cut from $1.225B to $1.150B bookings caused a one-day 40% stock decline",
        ],
        "defendant_officers": [
            "CEO Mark Pincus",
            "President John Schappert",
            "CFO David Wehner",
        ],
        "class_period_start": "2012-02-14",
        "class_period_end": "2012-07-25",
        "industry_sector": "Technology",
    },
    "In re Lumber Liquidators Holdings Securities Litigation": {
        "allegation_type": "product_safety_disclosure",
        "harm_theory": (
            "Lumber Liquidators failed to disclose that its Chinese-sourced laminate flooring "
            "contained formaldehyde levels exceeding California CARB Phase 2 standards, a fact "
            "known to management following internal testing. When CBS News 60 Minutes aired an "
            "investigative report on March 1, 2015 revealing the formaldehyde test results, "
            "the stock fell 25% in a single day, as investors were previously misled about the "
            "company's compliance with applicable safety standards."
        ),
        "key_allegations": [
            "Internal quality testing revealed CARB non-compliance before the CBS News investigation",
            "The company's SEC filings represented that products complied with all applicable regulations",
            "Management knew of formaldehyde levels exceeding CARB Phase 2 limits by 2-7 times",
            "Chinese supplier contracts required compliance representations that the company failed to audit",
            "The March 2015 60 Minutes broadcast constituted a corrective disclosure, causing a 25% stock decline",
        ],
        "defendant_officers": ["CEO Robert Lynch", "CFO Daniel Terrell"],
        "class_period_start": "2013-02-22",
        "class_period_end": "2015-03-26",
        "industry_sector": "Retail",
    },
    "In re Valeant Pharmaceuticals International Securities Litigation": {
        "allegation_type": "accounting_fraud",
        "harm_theory": (
            "Valeant concealed a secret network of specialty pharmacies, led by Philidor Rx "
            "Services, through which the company channel-stuffed products and recorded revenue "
            "from transactions that were not arm's-length sales. This scheme allowed Valeant to "
            "present consistent organic growth in an acquisition-heavy model; when Citron Research "
            "published its analysis of the Philidor relationship in October 2015, the stock declined "
            "from $262 to $73 over the following month, destroying $60 billion in market value."
        ),
        "key_allegations": [
            "Valeant held an undisclosed option to acquire Philidor and consolidated its operations without disclosure",
            "Products shipped to Philidor were recorded as revenue even though they were not sold to end patients",
            "Valeant's organic growth figures were artificially inflated by channel-stuffing through Philidor",
            "The company failed to disclose the Philidor relationship in its periodic SEC filings",
            "Internal emails showed executives knew the Philidor arrangement was structured to avoid accounting consolidation",
        ],
        "defendant_officers": [
            "CEO J. Michael Pearson",
            "CFO Howard Schiller",
            "CFO Robert Rosiello",
        ],
        "class_period_start": "2013-02-28",
        "class_period_end": "2015-10-30",
        "industry_sector": "Healthcare",
    },
    "In re Kraft Heinz Securities Litigation": {
        "allegation_type": "revenue_recognition",
        "harm_theory": (
            "Kraft Heinz artificially reduced its cost of goods sold and inflated procurement "
            "savings metrics through improper accounting for supplier contracts, rebates, and "
            "accruals in its procurement function. The scheme allowed the company to report "
            "adjusted EBITDA figures that were not achievable through legitimate operations; when "
            "Kraft Heinz disclosed in February 2019 an SEC subpoena and a $15.4 billion goodwill "
            "impairment charge, the stock declined 27% in a single day, its largest single-day "
            "decline since the 2015 merger."
        ),
        "key_allegations": [
            "Kraft Heinz misstated procurement savings by improperly recognizing supplier rebates",
            "Accruals in the procurement function were manipulated to smooth reported financial results",
            "The company failed to disclose an SEC investigation into its accounting practices until February 2019",
            "Goodwill impairments of $15.4 billion reflected overvalued brand assets propped up by accounting manipulation",
            "3G Capital's cost-cutting methodology created pressure to record savings that had not been achieved",
        ],
        "defendant_officers": [
            "CEO Bernardo Hees",
            "CFO Paulo Basilio",
            "CFO David Knopf",
        ],
        "class_period_start": "2016-07-06",
        "class_period_end": "2019-02-21",
        "industry_sector": "Consumer",
    },
    "In re General Electric Company Securities Litigation": {
        "allegation_type": "accounting_fraud",
        "harm_theory": (
            "GE concealed mounting liabilities in its insurance run-off portfolio and its power "
            "division through years of inadequate reserves and improper accounting. The company "
            "repeatedly assured investors that its industrial free cash flow supported its "
            "dividend; when GE disclosed an $8.3 billion after-tax insurance charge and dividend "
            "cut in January 2018, followed by a $22 billion goodwill impairment in October 2018, "
            "the stock declined from $31 to $6, destroying approximately $150 billion in market "
            "capitalization and vindicating the fraud alleged in this complaint."
        ),
        "key_allegations": [
            "GE's long-term care insurance reserves were systemically understated for years",
            "The power division's service agreements were accounted for under overly optimistic assumptions",
            "Industrial free cash flow figures were manipulated by classifying items between operating segments",
            "Management knew of the reserve deficiency in GE Capital's insurance run-off portfolio by 2016",
            "GE misled investors about the adequacy of its $15 billion insurance reserve by 16 months",
        ],
        "defendant_officers": [
            "Former CEO Jeffrey Immelt",
            "CEO John Flannery",
            "CFO Jamie Miller",
        ],
        "class_period_start": "2015-07-17",
        "class_period_end": "2018-01-24",
        "industry_sector": "Finance",
    },
    "Sjunde AP-Fonden v. Goldman Sachs Group, Inc.": {
        "allegation_type": "disclosure_failure",
        "harm_theory": (
            "Goldman Sachs failed to disclose that senior executives, including 1MDB bond deal "
            "bankers, knew or recklessly disregarded that proceeds from $6.5 billion in bonds "
            "Goldman underwrote for the Malaysian sovereign fund 1MDB would be diverted through "
            "bribery and theft. This omission allowed Goldman to collect $600 million in fees "
            "while exposing the firm to criminal liability that eventually resulted in a $2.9 "
            "billion DOJ settlement, causing Goldman's stock to trade at artificially inflated "
            "prices throughout the class period."
        ),
        "key_allegations": [
            "Goldman senior bankers knew that 1MDB bond proceeds were being diverted from their stated purpose",
            "The company paid and received bribes channeled through sovereign wealth fund bond deals",
            "Goldman's compliance function failed to apply adequate anti-corruption due diligence",
            "SEC and DOJ filings were false by omission regarding the firm's criminal liability exposure",
            "The November 2018 DOJ indictment of Goldman's former Southeast Asia chairman constituted a corrective disclosure",
        ],
        "defendant_officers": [
            "CEO Lloyd Blankfein",
            "CEO David Solomon",
            "Former Partner Tim Leissner",
        ],
        "class_period_start": "2012-05-18",
        "class_period_end": "2018-12-17",
        "industry_sector": "Finance",
    },
}


def extract_complaint(text: str, case_name: str) -> dict:
    """
    Extract allegation type and harm theory from complaint text using Claude.

    In DEMO_MODE, returns pre-baked results keyed by case_name.
    In live mode, calls Claude with the complaint text.
    """
    if DEMO_MODE:
        return _DEMO_EXTRACTIONS.get(case_name, _default_extraction(case_name))

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Extract structured information from this securities complaint:\n\n{text[:6000]}",
            }],
        )
        raw = msg.content[0].text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        # Validate allegation_type
        from config import ALLEGATION_TYPES
        if data.get("allegation_type") not in ALLEGATION_TYPES:
            data["allegation_type"] = "disclosure_failure"
        return data
    except Exception as exc:
        return _error_extraction(case_name, str(exc))


def _default_extraction(case_name: str) -> dict:
    return {
        "allegation_type": "disclosure_failure",
        "harm_theory": f"Extraction not available for {case_name} in demo mode.",
        "key_allegations": [],
        "defendant_officers": [],
        "class_period_start": None,
        "class_period_end": None,
        "industry_sector": "Other",
    }


def _error_extraction(case_name: str, error: str) -> dict:
    return {
        "allegation_type": "disclosure_failure",
        "harm_theory": f"Extraction failed: {error[:200]}",
        "key_allegations": [],
        "defendant_officers": [],
        "class_period_start": None,
        "class_period_end": None,
        "industry_sector": "Other",
    }
