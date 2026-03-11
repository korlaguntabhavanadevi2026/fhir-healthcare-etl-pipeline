---
layout: default
title: FHIR-Driven ETL Pipeline for Healthcare Data Interoperability – BPMN Model
---

# BPMN Model

[Home](./index.md) ·· [BPMN Model](./bpmn.md) ·· [ETL Pipeline](./etl_pipeline.md) ·· [Insights](./insights.md) ·· [Team Contributions](./team_contrib.md) ·· [About](./about.md)

---

![BPMN Model](/assets/Group_BPMN.png)

[Click on this link to view our BPMN Model](https://modeler.camunda.io/share/0627bcda-82bf-456d-8332-1b807294b298)


---


## Overview

The BPMN (Business Process Model and Notation) diagram models a real-world scenario where a **Primary Care Clinic** refers a patient to a **Specialist Hospital** and the two entities coordinate care across systems. This process visualization helps standardize workflows and supports healthcare interoperability initiatives.

---

## BPMN Workflow Explanation

### **1. Referral from Primary Care**

- The process begins with a **Start Event** at the Primary Care Clinic.
- A **Patient Referral Sub-Process** is initiated, where the clinic **sends referral details** (including medical history and referral reasons) to the hospital.
- A **Message Flow** transmits this information to the hospital, triggering an **Intermediate Message Event**.

### **2. Hospital Specialist Care**

- The hospital **receives and reviews the referral** to ensure completeness.
- If the referral is accepted, the **Specialist Treatment Sub-Process** begins:
  - The hospital **registers the patient** in its system.
  - A specialist **evaluates and treats** the patient.
- A **Parallel Gateway** then determines the outcome:
  - If **further care is required**, the hospital refers the patient back to the clinic with detailed updates.
  - If the **issue is resolved**, the hospital discharges the patient but still **communicates treatment details** back to the clinic.

### **3. Follow-Up by Primary Care Clinic**

- The clinic **receives the treatment details** via another **Intermediate Message Event**.
- It then **updates patient records** accordingly.
- A **Decision Gateway** evaluates whether a follow-up is needed:
  - If yes, the clinic **schedules follow-up care**.
  - If no further action is needed, the process concludes.

---

## Why BPMN Matters

This BPMN model offers a **clear, standardized view** of inter-organizational healthcare workflows, facilitating better communication between systems and stakeholders. By modeling these interactions visually, we ensure all critical decision points, message flows, and outcomes are traceable—supporting both technical implementation and clinical coordination.
