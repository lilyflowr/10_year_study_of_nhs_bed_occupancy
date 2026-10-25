---The Macro Trend (National): What is happening to overall capacity and occupancy year over year?---
SELECT
    year,
    SUM(available_gen_acute) AS total_available_gen_acute,
    SUM(occupied_gen_acute)	AS total_occupied_gen_acute,
    ROUND((SUM(occupied_gen_acute) / SUM(available_gen_acute)) * 100, 2) AS average_occupied_percentage
FROM nhs_bed_occupancy
GROUP BY year
ORDER BY year ASC;

---The Micro Trend (Trust-Level): Which specific hospitals are in crisis, and which have headroom?---
---TOP 10 IN CRISIS
SELECT
   org_code,
   org_name,
   region_code,
   ROUND((SUM(occupied_gen_acute)/SUM(available_gen_acute)) * 100,2) AS average_occupied_percentage
FROM nhs_bed_occupancy
WHERE (available_gen_acute > 0) 
    AND year = '2025-26'
GROUP BY org_code, org_name, region_code
ORDER BY average_occupied_percentage DESC
LIMIT 10;

---TOP 10 IN IN GOOD SHAPE
---resulted in bringing up trusts that are specialized even though they had gen and acute wards
SELECT
    org_code,
	org_name,
	region_code,
    ROUND((SUM(occupied_gen_acute)/SUM(available_gen_acute)) * 100,2) AS average_occupied_percentage
FROM nhs_bed_occupancy
WHERE (available_gen_acute >0)
    AND year = '2025-26'
GROUP BY org_code,org_name, region_code
ORDER BY average_occupied_percentage ASC
LIMIT 10;

------ How do General & Acute beds compare to specialist beds?
SELECT 
   year,
    ROUND((SUM(occupied_gen_acute) / SUM(available_gen_acute)) * 100, 2) AS gen_acute_occ_pct,
    ROUND((SUM(occupied_mental) / SUM(available_mental)) * 100, 2) AS mental_health_occ_pct,
    ROUND((SUM(occupied_maternity) / SUM(available_maternity)) * 100, 2) AS maternity_occ_pct,
    ROUND((SUM(occupied_ld) / SUM(available_ld)) * 100, 2) AS ld_occ_pct
FROM nhs_bed_occupancy
GROUP BY year 
ORDER BY year ASC;
