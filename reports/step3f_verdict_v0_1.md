# Step 3-F Additional Sample Verification v0.1

## 0. Purpose
- This report records Claude's Step 3-F verification result.
- It is not a buy/sell recommendation.
- It does not confirm v0.3 hard filter rules.
- It does not modify universe_master.csv or audit CSV.
- It is a verification record for additional samples.

## 1. Current Status
- universe_master.csv v0.2 repair completed.
- universe_quality_audit v0.1 completed.
- Step 3 sample and metadata diagnosis records committed and pushed.
- Step 3-F additional sample extraction completed.
- Input sample file: reports/step3f_additional_samples_v0_1.csv
- SNDK/INTC metadata track remains separate and on hold.
- No operating code changes.

## 2. Final Verdict
- Verdict: CONDITIONAL PASS
- Reason:
  Classification system worked consistently.
  No clear MISCLASSIFIED rows were found.
  However, a classification asymmetry was found between US ADRs and Korean domestic stocks under $10B market cap.
  foreign_ownership_pct exists in audit data but is not being used in classification.
  Additional diagnosis is required before v0.3 hard filter design.

## 3. Overall Summary
- Total samples: 39
- OK: 33
- NEED_DATA: 3
- MISCLASSIFIED: 0
- HARD_FILTER_CANDIDATE: 3
- Main issue:
  US ADRs under $10B can remain EXTENDED, while Korean domestic stocks under $5B are pushed to DISCOVERY_ONLY.
- Main check point:
  foreign_ownership_pct is present in the audit data but not used in classification.

## 4. Axis Findings

### 4.1 ADR Classification Consistency
- ADR rule creation is not recommended at this stage.
- ADR classification appears mostly driven by market cap.
- $250B+ ADRs such as TSM / ASML / SAP / BABA / TM are CORE.
- Smaller ADRs such as FER / CCEP / TRI / ABEV / BBD / CPNG / PKX are EXTENDED.
- ASR around $8B is EXTENDED.
- Non-ADR references such as JPM / MSFT are CORE.
- Do not create a rule such as "ADR cannot be CORE".
- Such a rule would break on TSM / ASML type mega-cap ADRs.

### 4.2 Korean Domestic Quality Stock Standard
- Rule confirmation is still on hold due to limited cases.
- Korean domestic stocks over $10B such as KT, SK Telecom, KEPCO, KT&G, KB Financial, Samsung Life are EXTENDED.
- Korean domestic stocks below $5B such as LG Uplus and Macquarie Korea Infrastructure are DISCOVERY_ONLY.
- Similar-size US ADR ASR around $8B is EXTENDED.
- This reveals US/KR asymmetry below $10B.
- Do not automatically upgrade Korean domestic stocks.
- Additional data is needed.

### 4.3 HEALTHCARE_EVENT_RISK + CORE
- annotate-only treatment is recommended.
- HC_EVENT_CORE samples such as UNH / TMO / ISRG are large-cap CORE names.
- HC_EVENT_EXTENDED samples are mostly $30B to $50B mid-large cap Health Care names.
- Large Pharma references such as LLY / JNJ have no HEALTHCARE_EVENT_RISK flag and remain CORE.
- HEALTHCARE_EVENT_RISK appears broad and sub_industry-based.
- Do not convert HEALTHCARE_EVENT_RISK into a hard block rule.

## 5. Problem Rows / NEED_DATA

| sample_id | ticker | name | current_role | risk_level | sample_reason_code | verdict | hard_filter_candidate | reason | needed_data |
|---|---|---|---|---|---|---|---|---|---|
| S3F-013 | ASR | Grupo Aeroportuario del Sureste | EXTENDED | MEDIUM | ADR_EXTENDED | OK | YES | $8B ADR remains EXTENDED while similar-size Korean domestic examples are DISCOVERY_ONLY. This shows US/KR asymmetry. | trading_liquidity, dividend_history, ADR/KR classification consistency |
| S3F-018 | 032640.KS | LG Uplus | DISCOVERY_ONLY | HIGH | KR_DOMESTIC_TELECOM | NEED_DATA | YES | Major Korean telecom, foreign_ownership_pct 25, market cap $4.8B, pushed to DISCOVERY_ONLY. | operating_income_stability, dividend_history, domestic_market_share, trading_liquidity |
| S3F-020 | 088980.KS | Macquarie Korea Infrastructure | DISCOVERY_ONLY | HIGH | KR_DOMESTIC_INFRA | NEED_DATA | YES | Infrastructure fund with foreign_ownership_pct 30 and stable dividend profile, but pushed to DISCOVERY_ONLY by market cap. | dividend_history, fund_structure, NAV_volatility, trading_liquidity |
| S3F-027 | UNH | UnitedHealth Group | CORE | LOW | HC_EVENT_CORE | NEED_DATA | NO | Large-cap CORE classification is consistent, but recent real-world events are not visible in metadata. | recent_event, litigation_status, regulatory_status |
| S3F-038 | AMGN | Amgen Inc. | EXTENDED | MEDIUM | HC_BIOTECH_BOUNDARY | OK | YES | Large Biotech remains EXTENDED due to Biotechnology sub_industry; consistent with GILD/ABBV pattern. | revenue_concentration, patent_expiry |
| S3F-039 | GILD | Gilead Sciences | EXTENDED | MEDIUM | HC_BIOTECH_BOUNDARY | OK | YES | Large Biotech remains EXTENDED; same pattern as AMGN. | revenue_concentration, patent_expiry |

## 6. OK Summary
- ADR related OK:
  TSM, ASML, SAP, BABA, TM, CPNG, PKX, FER, CCEP, TRI, ABEV, BBD.
- Korean domestic OK:
  KT, SK Telecom, KEPCO, KB Financial, Samsung Life, KT&G.
- KOSDAQ theme OK:
  Simmtech, Robotis, Voronoi.
- HEALTHCARE_EVENT_RISK OK:
  TMO, ISRG, EW, CAH, IDXX, BDX, HUM, WAT.
- Reference OK:
  JPM, MSFT, LLY, JNJ.

## 7. Hard Filter Candidate Patterns
Important:
These are not confirmed v0.3 rules.

### Candidate 1: US/KR asymmetry under $10B market cap
- Related samples: ASR, LG Uplus, Macquarie Korea Infrastructure.
- Pattern:
  Similar market-cap range but different classification by market/listing type.
- Status:
  Strongest pattern. Needs additional diagnosis.
- Required data:
  foreign_ownership_pct, dividend_history, trading_liquidity.

### Candidate 2: foreign_ownership_pct usage
- Related samples:
  KT, SK Telecom, KB Financial, Samsung Life, KT&G.
- Pattern:
  foreign_ownership_pct exists but is not used in audit classification.
- Status:
  Needs fill-rate and threshold simulation before rule design.
- Required data:
  foreign_ownership_pct coverage across all 656 audit rows.

### Candidate 3: Large Biotech classification ceiling
- Related samples:
  AMGN, GILD, ABBV.
- Pattern:
  Large Biotech remains EXTENDED even above $150B market cap.
- Status:
  Needs user risk-definition decision.
- Required data:
  revenue_concentration, patent_expiry, pipeline dependence.

## 8. GPT Review Points
- Do not overfit from 1-3 cases.
- Do not create an ADR hard block rule.
- Do not convert HEALTHCARE_EVENT_RISK into a hard block rule.
- Do not automatically upgrade Korean domestic stocks.
- foreign_ownership_pct threshold is arbitrary unless simulated.
- Check how many of 656 audit rows have foreign_ownership_pct populated.
- Check whether Korean sub-$5B stable domestic names exist beyond LG Uplus and Macquarie Korea Infrastructure.
- trading_liquidity and dividend_history are not currently available in audit and should be checked before rule design.

## 9. Next Steps
- Commit reports/step3f_additional_samples_v0_1.csv together with this verdict report after GPT/Claude review.
- Run foreign_ownership_pct fill-rate diagnosis.
- Run Korean sub-$5B stable domestic candidate extraction if needed.
- v0.3 hard filter design is still not allowed.
- Do not modify universe_master.csv.
- Do not modify audit CSV.
- Do not modify operating code.
- Do not resume SNDK/INTC metadata track in this step.

## 10. Prohibited Actions
- No v0.3 hard filter code.
- No audit CSV modification.
- No universe_master.csv modification.
- No operating code modification.
- No buy/sell/recommendation language.
- No immediate application to v1.1.1 runtime.
- No git add/commit/push in this task.

## 11. Git Status
- git status -sb:
  `## main...origin/main`
  `?? backups/`
  `?? reports/step3f_additional_samples_v0_1.csv`
  `?? reports/step3f_verdict_v0_1.md`
- git status --short:
  `?? backups/`
  `?? reports/step3f_additional_samples_v0_1.csv`
  `?? reports/step3f_verdict_v0_1.md`
- git add status: NO
- commit status: NO
- push status: NO
