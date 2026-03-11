---
layout: default
title: FHIR-Driven ETL Pipeline for Healthcare Data Interoperability
---

# Home

[Home](index.md)   ·· [BPMN Model](./bpmn.md)   ·· [ETL Pipeline](./etl_pipeline.md)   ·· [Insights](insights.md)   ·· [Team Contributions](./team_contrib.md)   ·· [About](./about.md)

---

![image](/assets/logo.png)

## Project Overview

### **Goal**

Develop an automated ETL pipeline that:

- Extracts **Patient** and **Condition** resources (including parent- and child-term mapping via SNOMED CT) from an OpenEMR FHIR server.  
- Creates **Observation** (e.g., blood pressure) and **Procedure** resources when absent.  
- Loads and validates all resources on a Primary Care EHR FHIR endpoint.  
- Generates a simplified **HL7 v2 ADT** message for legacy-system interoperability.

### **Key Tools & Technologies**

- **FHIR APIs**: OpenEMR source and Primary Care target servers for resource CRUD and validation  
- **Python**:  
  - `requests` for FHIR interaction  
  - `hl7apy` for HL7 v2 message construction  
  - Custom ETL scripts for transformation logic  
- **Hermes Terminology Server**: SNOMED CT parent/child concept resolution  
- **BPMN**: Visual modeling of the patient-referral and treatment workflows  
- **GitHub Pages & Jekyll**: `jekyll-remote-theme` to host and style the project site

---

## Deliverables

1. **Automated ETL Pipeline**  
   - Patient & Condition extraction, transformation (parent/child mapping), and loading  
   - Observation and Procedure creation for vital signs and interventions  
   - HL7 v2 ADT message generation for downstream systems  

2. **Comprehensive Documentation**  
   - Detailed API endpoint specs, auth flows, and error-handling strategies  
   - Code snippets covering all five coding tasks (Parent, Child, Observation, Procedure, HL7 generation)  

3. **BPMN Diagram**  
   - Illustrates referral, specialist treatment, communication, and follow-up processes  

4. **Insights & Visualizations**  
   - Key findings (e.g., patient demographics, condition prevalence)  
   - Sample charts demonstrating clinical data trends  

5. **Team Contributions & Reflections**  
   - Roles, individual tasks, and lessons learned from cross-disciplinary collaboration
