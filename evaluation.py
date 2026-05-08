from langsmith import Client

client=Client()

examples=[
    {
        "inputs":{"query":"What were Apple's total net sales for the first quarter of fiscal 2026?"},
        "outputs":{"answer":"For the three months ended December 27, 2025, Apple reported total net sales of $143,756 million."}
    },
    {
        "inputs":{"query":"How much net income did Apple report in Q1 2026?"},
        "outputs":{"answer":"Apple reported net income of $42,097 million for the first quarter of 2026."}
    },
    {
        "inputs":{"query":"What was the diluted earnings per share (EPS) for the quarter ended December 27, 2025?"},
        "outputs":{"answer":"The diluted earnings per share for the first quarter of 2026 was $2.84."}
    },
    {
        "inputs":{"query":"How many shares of common stock were issued and outstanding as of January 16, 2026?"},
        "outputs":{"answer":"As of January 16, 2026, there were 14,681,140,000 shares of common stock issued and outstanding."}
    },
    {
        "inputs":{"query":"What was the total cash, cash equivalents, and marketable securities balance as of December 27, 2025?"},
        "outputs":{"answer":"As of December 27, 2025, the total was $144,795 million, consisting of $45,317 million in cash and cash equivalents, $21,590 million in current marketable securities, and $77,888 million in non-current marketable securities."}
    },
    {
        "inputs":{"query":"Which product category generated the highest net sales in Q1 2026?"},
        "outputs":{"answer":"The iPhone generated the highest net sales at $85,269 million."}
    },
    {
        "inputs":{"query":"What was the year-over-year percentage change in iPhone net sales?"},
        "outputs":{"answer":"iPhone net sales increased by 23% compared to the first quarter of 2025."}
    },
    {
        "inputs":{"query":"Why did Mac net sales decrease in Q1 2026?"},
        "outputs":{"answer":"Mac net sales decreased primarily due to lower net sales of laptops and desktops."}
    },
    {
        "inputs":{"query":"What was the total net sales for the Services segment in Q1 2026?"},
        "outputs":{"answer":"Services net sales were $30,013 million for the first quarter of 2026."}
    },
    {
        "inputs":{"query":"What drivers contributed to the increase in Services net sales?"},
        "outputs":{"answer":"The increase was primarily driven by higher net sales from advertising, the App Store, and cloud services."}
    },
    {
        "inputs":{"query":"What was the total gross margin percentage for Apple in Q1 2026?"},
        "outputs":{"answer":"Apple's total gross margin percentage was 48.2%."}
    },
    {
        "inputs":{"query":"Compare the Products gross margin percentage between Q1 2026 and Q1 2025."},
        "outputs":{"answer":"The Products gross margin percentage was 40.7% in Q1 2026, compared to 39.3% in Q1 2025."}
    },
    {
        "inputs":{"query":"What was the Services gross margin percentage in Q1 2026?"},
        "outputs":{"answer":"The Services gross margin percentage was 76.5%."}
    },
    {
        "inputs":{"query":"How much did Apple spend on Research and Development in Q1 2026?"},
        "outputs":{"answer":"Apple spent $10,887 million on research and development."}
    },
    {
        "inputs":{"query":"What factors drove the 32% increase in R&D expenses?"},
        "outputs":{"answer":"The growth was primarily driven by increases in infrastructure-related costs, headcount-related expenses, and engineering program costs."}
    },
    {
        "inputs":{"query":"What was the net sales amount for the Greater China segment in Q1 2026?"},
        "outputs":{"answer":"Net sales in Greater China were $25,526 million."}
    },
    {
        "inputs":{"query":"What was the year-over-year percentage increase for Greater China net sales?"},
        "outputs":{"answer":"Greater China net sales increased by 38% year-over-year."}
    },
    {
        "inputs":{"query":"Which geographic segment had the highest net sales in Q1 2026?"},
        "outputs":{"answer":"The Americas segment had the highest net sales at $58,529 million."}
    },
    {
        "inputs":{"query":"What was the impact of foreign currency on Europe's net sales in Q1 2026?"},
        "outputs":{"answer":"The strength of foreign currencies relative to the U.S. dollar had a net favorable year-over-year impact on Europe net sales."}
    },
    {
        "inputs":{"query":"How did the Japanese yen's performance affect Japan's net sales?"},
        "outputs":{"answer":"The weakness in the yen relative to the U.S. dollar had an unfavorable year-over-year impact on Japan net sales."}
    },
    {
        "inputs":{"query":"What was the total amount of common stock repurchased by Apple during Q1 2026?"},
        "outputs":{"answer":"Apple repurchased $25.0 billion (or 93 million shares) of its common stock during the quarter."}
    },
    {
        "inputs":{"query":"What was the total amount paid for dividends and dividend equivalents in Q1 2026?"},
        "outputs":{"answer":"Apple paid $3.9 billion in dividends and dividend equivalents during the first quarter of 2026."}
    },
    {
        "inputs":{"query":"What is the current quarterly cash dividend per share?"},
        "outputs":{"answer":"The quarterly cash dividend is $0.26 per share."}
    },
    {
        "inputs":{"query":"What were the total manufacturing purchase obligations as of December 27, 2025?"},
        "outputs":{"answer":"Total manufacturing purchase obligations were $44.4 billion."}
    },
    {
        "inputs":{"query":"How much of the manufacturing purchase obligations are payable within 12 months?"},
        "outputs":{"answer":"$43.7 billion of the manufacturing purchase obligations are payable within 12 months."}
    },
    {
        "inputs":{"query":"What was the total for 'Other Purchase Obligations' as of December 27, 2025?"},
        "outputs":{"answer":"Total other purchase obligations were $35.1 billion."}
    },
    {
        "inputs":{"query":"What was the amount of commercial paper outstanding as of December 27, 2025?"},
        "outputs":{"answer":"The commercial paper outstanding was $2.0 billion."}
    },
    {
        "inputs":{"query":"What was the carrying amount of Apple's total term debt as of December 27, 2025?"},
        "outputs":{"answer":"The total term debt was $88.5 billion, comprising $11.8 billion in current term debt and $76.7 billion in non-current term debt."}
    },
    {
        "inputs":{"query":"What was the fair value of Apple's Notes (term debt) as of December 27, 2025?"},
        "outputs":{"answer":"The fair value of the Notes was $78.1 billion, based on Level 2 inputs."}
    },
    {
        "inputs":{"query":"What was Apple's effective tax rate for Q1 2026?"},
        "outputs":{"answer":"The effective tax rate for Q1 2026 was 17.5%."}
    },
    {
        "inputs":{"query":"Why was the Q1 2026 effective tax rate lower than the statutory federal rate?"},
        "outputs":{"answer":"It was lower primarily due to a lower effective tax rate on foreign earnings, the U.S. federal R&D credit, and tax benefits from share-based compensation."}
    },
    {
        "inputs":{"query":"Why did the effective tax rate increase from 14.7% in Q1 2025 to 17.5% in Q1 2026?"},
        "outputs":{"answer":"The increase was primarily due to foreign currency loss regulations issued in December 2024 and the tax impact from foreign currency revaluations related to the State Aid Decision in the prior year."}
    },
    {
        "inputs":{"query":"What was the total comprehensive income for Q1 2026?"},
        "outputs":{"answer":"Total comprehensive income was $42,814 million."}
    },
    {
        "inputs":{"query":"How much cash was generated by operating activities in Q1 2026?"},
        "outputs":{"answer":"Apple generated $53,925 million in cash from operating activities."}
    },
    {
        "inputs":{"query":"What were the total assets reported as of December 27, 2025?"},
        "outputs":{"answer":"Total assets were $379,297 million."}
    },
    {
        "inputs":{"query":"What was the net balance of accounts receivable as of December 27, 2025?"},
        "outputs":{"answer":"The net accounts receivable balance was $39,921 million."}
    },
    {
        "inputs":{"query":"How much inventory did Apple hold at the end of Q1 2026?"},
        "outputs":{"answer":"Apple held $5,875 million in inventories as of December 27, 2025."}
    },
    {
        "inputs":{"query":"What was the net value of property, plant, and equipment as of December 27, 2025?"},
        "outputs":{"answer":"The net property, plant, and equipment value was $50,159 million."}
    },
    {
        "inputs":{"query":"What was the total amount of current liabilities as of December 27, 2025?"},
        "outputs":{"answer":"Total current liabilities were $162,367 million."}
    },
    {
        "inputs":{"query":"What was the total shareholders' equity at the end of the quarter?"},
        "outputs":{"answer":"Total shareholders' equity was $88,190 million."}
    },
    {
        "inputs":{"query":"How much was the accumulated deficit as of December 27, 2025?"},
        "outputs":{"answer":"The accumulated deficit was $2,177 million."}
    },
    {
        "inputs":{"query":"Which customers represented 10% or more of total trade receivables?"},
        "outputs":{"answer":"As of December 27, 2025, two customers individually represented 15% and 10% of total trade receivables."}
    },
    {
        "inputs":{"query":"What percentage of trade receivables was accounted for by third-party cellular network carriers?"},
        "outputs":{"answer":"Third-party cellular network carriers accounted for 35% of total trade receivables."}
    },
    {
        "inputs":{"query":"How does Apple define 'vendor non-trade receivables'?"},
        "outputs":{"answer":"These are receivables from manufacturing vendors resulting from the sale of components to those vendors who then assemble final products for Apple."}
    },
    {
        "inputs":{"query":"What was the fair value of level 1 money market funds as of December 27, 2025?"},
        "outputs":{"answer":"The fair value of level 1 money market funds was $5,959 million."}
    },
    {
        "inputs":{"query":"What was the total notional amount of derivative instruments not designated as accounting hedges?"},
        "outputs":{"answer":"As of December 27, 2025, the total notional amount for foreign exchange contracts not designated as accounting hedges was $120,980 million."}
    },
    {
        "inputs":{"query":"What products were updated or announced during the first quarter of 2026?"},
        "outputs":{"answer":"Apple announced updated 14-inch MacBook Pro, iPad Pro, and Apple Vision Pro models."}
    },
    {
        "inputs":{"query":"What fine was imposed on Apple by the European Commission on April 23, 2025?"},
        "outputs":{"answer":"The European Commission fined Apple €500 million in the Article 5(4) DMA Investigation."}
    },
    {
        "inputs":{"query":"What is the status of the DOJ civil antitrust lawsuit against Apple?"},
        "outputs":{"answer":"The DOJ and several attorneys general filed a lawsuit alleging monopolization in smartphone markets; Apple believes it has substantial defenses and intends to defend itself vigorously."}
    },
    {
        "inputs":{"query":"What was the Ninth Circuit Court's ruling regarding the 2025 Injunction in the Epic Games case?"},
        "outputs":{"answer":"The court upheld the injunction in part, allowing Apple to require parity in size/form for links but also held that Apple can charge a commission on link-out purchases."}
    },
    {
        "inputs":{"query":"Who is Apple's current Chief Financial Officer as of the report date?"},
        "outputs":{"answer":"Kevan Parekh is the Senior Vice President and Chief Financial Officer."}
    },
    {
        "inputs":{"query":"What are the details of Kevan Parekh's Rule 10b5-1 trading plan?"},
        "outputs":{"answer":"Entered on November 21, 2025, it provides for the sale of shares vesting between April 15, 2026, and October 15, 2026, and expires on December 31, 2026."}
    },
    {
        "inputs":{"query":"When does Apple plan to adopt ASU 2024-03 regarding expense disaggregation?"},
        "outputs":{"answer":"Apple will adopt ASU 2024-03 in its fourth quarter of 2028 using a prospective transition method."}
    },
    {
        "inputs":{"query":"What will ASU 2023-09 require Apple to disclose regarding income taxes?"},
        "outputs":{"answer":"It will require additional information in the income tax rate reconciliation and disaggregated income taxes paid by federal, state, and foreign jurisdictions."}
    },
    {
        "inputs":{"query":"What was the total unrecognized compensation cost for outstanding RSUs as of December 27, 2025?"},
        "outputs":{"answer":"The total unrecognized compensation cost was $31.5 billion, to be recognized over approximately 2.9 years."}
    },
    {
        "inputs":{"query":"What was the weighted-average grant-date fair value per RSU for units granted in Q1 2026?"},
        "outputs":{"answer":"The weighted-average grant-date fair value was $256.22 per RSU."}
    },
    {
        "inputs":{"query":"What was the total amount of cash paid for income taxes, net, in Q1 2026?"},
        "outputs":{"answer":"Apple paid $3,434 million in cash for income taxes, net."}
    },
    {
        "inputs":{"query":"What was the operating income for the Japan segment in Q1 2026?"},
        "outputs":{"answer":"Japan's operating income was $4,613 million."}
    },
    {
        "inputs":{"query":"How much did operating income increase for the Americas segment year-over-year?"},
        "outputs":{"answer":"Americas operating income increased from $21,509 million in Q1 2025 to $23,953 million in Q1 2026."}
    },
    {
        "inputs":{"query":"What was the total change in unrealized gains/losses on marketable debt securities, net of tax, for Q1 2026?"},
        "outputs":{"answer":"There was a total change of $428 million (gain) in Q1 2026."}
    },
    {
        "inputs":{"query":"What is the maximum length of time Apple is hedging its exposure for term debt–related foreign currency transactions?"},
        "outputs":{"answer":"The maximum length is 17 years."}
    },
    {
        "inputs":{"query":"What does Apple use to protect gross margins from fluctuations in foreign exchange rates?"},
        "outputs":{"answer":"Apple may use forwards, options, or other instruments and may designate them as cash flow hedges."}
    },
    {
        "inputs":{"query":"What was the carrying amount of term debt subject to fair value hedges as of December 27, 2025?"},
        "outputs":{"answer":"The carrying amount was $12.6 billion."}
    },
    {
        "inputs":{"query":"How much did Apple spend on the acquisition of property, plant, and equipment in Q1 2026?"},
        "outputs":{"answer":"Apple spent $2,373 million on the acquisition of property, plant, and equipment."}
    },
    {
        "inputs":{"query":"What was the total number of RSUs that vested during the first quarter of 2026?"},
        "outputs":{"answer":"33.905 million RSUs vested during the quarter."}
    },
    {
        "inputs":{"query":"What percentage of non-current mortgage- and asset-backed securities have maturities greater than 10 years?"},
        "outputs":{"answer":"70% of these securities have maturities greater than 10 years."}
    },
    {
        "inputs":{"query":"What was the balance of deferred revenue as of December 27, 2025?"},
        "outputs":{"answer":"Total deferred revenue was $14.3 billion."}
    },
    {
        "inputs":{"query":"What percentage of deferred revenue does Apple expect to realize within one year?"},
        "outputs":{"answer":"Apple expects 66% of total deferred revenue to be realized in less than a year."}
    },
    {
        "inputs":{"query":"Which accounting standard update modernizes the accounting for internal-use software?"},
        "outputs":{"answer":"ASU No. 2025-06, Intangibles—Goodwill and Other—Internal-Use Software (Subtopic 350-40)."}
    },
    {
        "inputs":{"query":"What was the total other comprehensive income for the quarter ended December 28, 2024?"},
        "outputs":{"answer":"Total other comprehensive income for that quarter was $383 million."}
    },
    {
        "inputs":{"query":"How many vendors individually represented 10% or more of total vendor non-trade receivables at the end of 2025?"},
        "outputs":{"answer":"Two vendors represented 47% and 26% of total vendor non-trade receivables."}
    },
    {
        "inputs":{"query":"What was the total amount of dividends and dividend equivalents declared per share/RSU in Q1 2026?"},
        "outputs":{"answer":"The amount declared was $0.26 per share or RSU."}
    },
    {
        "inputs":{"query":"What is the par value of Apple's common stock?"},
        "outputs":{"answer":"The par value is $0.00001 per share."}
    },
    {
        "inputs":{"query":"What was the total value of RSUs that vested during Q1 2026?"},
        "outputs":{"answer":"The total vesting-date fair value of RSUs was $8.6 billion."}
    },
    {
        "inputs":{"query":"Where is Apple Inc.'s principal executive office located?"},
        "outputs":{"answer":"One Apple Park Way, Cupertino, California 95014."}
    }
]

dataset_name="Vector RAG"
dataset=client.create_dataset(dataset_name=dataset_name)
client.create_examples(
    dataset_id=dataset.id,
    examples=examples
)