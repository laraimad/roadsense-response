# Demo Script: 3-5 Minutes

## 0:00-0:30 - Problem

"My FYP detects potholes from camera and vehicle sensor evidence. For this challenge, I focused on the next product problem: how a road operator turns detections into repair decisions. RoadSense Response is a separate, self-contained app with prepared demo data."

## 0:30-1:30 - Feature 1: Triage

1. Show the summary cards and explain that urgent means severity 70 or higher.
2. Search for `Jalan Teknokrat`, then filter to high severity incidents and clear the filters.
3. Select `RS-1042` from the map or queue.
4. Point out the source image, recommended action, model confidence, IMU impact, speed, and repeat detections.
5. Explain that the score is an experimental priority aid, not a validated road-safety measurement.

## 1:30-2:45 - Feature 2: Repair workflow

1. Change an incident from `Verified` to `Scheduled` or `In repair`.
2. Assign a maintenance team and add a short note.
3. Save, refresh the browser, and show that the update persists.
4. Show the new activity-history entry.
5. Export the CSV repair queue.
6. Show a dismissed false positive to demonstrate that the workflow handles uncertainty.

## 2:45-3:40 - Technical decisions

"The app uses Flask, vanilla JavaScript, and a local JSON store. I chose this stack for a fast, reliable reviewer setup. The UI and API are independent from my FYP; they do not import its models, raw logs, labels, or configuration. The app goes deep on two workflows instead of adding many incomplete features."

Show the `How it works` screen and briefly explain Detect, Prioritize, Respond.

## 3:40-4:20 - Challenges and next steps

"The hardest product decision was showing uncertain AI and sensor evidence without pretending the system is always correct. I kept a human verification step, exposed the evidence, and allowed false positives to be dismissed. With more time I would add login roles, a spatial database, mobile repair updates, audit history, and field validation of the severity model."

## Closing

"RoadSense Response turns a detection project into an operational workflow: understand the evidence, make a decision, and close the repair loop."
