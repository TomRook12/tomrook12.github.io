---
layout: post
title: Salesforce Summer '26
date: '2026-07-01'
author: tom
author_profile: /about/
categories: [Salesforce, Release Notes]
tags: [SalesforceFlow, Automation, Approvals, ReleaseNotes]
image: /assets/images/Salesforce_Summer_26/SalesforceSummer26Thumbnail.png
description: A round-up of the flow builder and approvals highlights from the Salesforce Summer '26 release, from date operators to smarter validation and error debugging.
---
# Salesforce Summer '26

Another 3rd of a year passed, another release another time for me to be late. But fear not dear viewer I remembered how to post and this information is just about relevant. If you haven't had a poke around yet allow me to take you on a tour of the best flow features that Summer '26 had to offer! 

## Use Date Operators in Decision Logic
Super cool logic! So many options, no more creating formulas or fields to try and perform these operations. If the field is date type (crucially not date time, so this doesn't work on Created Date for instance) then you can use:
- Is Today
- Is Anniversary of Today
- Last Number of Days

![Date operators available in a decision element for date fields](/assets/images/Salesforce_Summer_26/DataComparison.png)

[Use Date Operators in Decision Logic](https://help.salesforce.com/s/articleView?id=release-notes.rn_automate_flow_builder_use_date_operators_in_decision_logic.htm&release=262&type=5)

## Better flow errors
More flow love, less errors!
### Visualize the Execution Path When Testing a Screen Flow

Debugging in screen flow has long lagged behind the same helpful UI for record triggered flows, now this is a step in the right direction! This did throw me for a loop as they use the word "testing" in the release notes, however you can't create tests for screen flows... so "manually testing" is just debugging, don't know why they choose this language but they did. 

![Execution path visualized on the canvas while debugging a screen flow](/assets/images/Salesforce_Summer_26/DebugOnCanvasScreenflow.png)

[Visualize the Execution Path When Testing a Screen Flow](https://help.salesforce.com/s/articleView?id=release-notes.rn_automate_flow_builder_visualize_testing_path.htm&release=262&type=5)

### Review Flow Errors and Warnings with the Redesigned Validation Panel

No more getting interrupted mid flow as the validation panel can be brought up when you choose in draft flows. Issues are grouped by element as well, super handy!

[Review Flow Errors and Warnings with the Redesigned Validation Panel](https://help.salesforce.com/s/articleView?id=release-notes.rn_automate_flow_builder_redesigned_validation_panel.htm&release=262&type=5)

### Troubleshoot and Fix Flow Errors with Agentforce (Beta)

What do I make of this? Well it's certainly interesting, however there is an arduous amount of setup here for running an XML through an LLM. Even if Salesforce does provide the context.

[Troubleshoot and Fix Flow Errors with Agentforce (Beta)](https://help.salesforce.com/s/articleView?id=release-notes.rn_automate_flow_builder_troubleshoot_and_fix_flow_errors_with_agentforce_beta.htm&release=262&type=5)

## Identify Flow Version Changes at a Glance

Check what changed and what didn't when you view a flow! This is actually a very helpful feature that myself and a colleague used recently to have to work out how I had broken one of their flows, the UI I have to say is very nice.

View as a table:
![Flow version differences shown in a comparison table](/assets/images/Salesforce_Summer_26/FlowComparisonTable.png)
View on the canvas:
![Flow version differences shown on the canvas view](/assets/images/Salesforce_Summer_26/FlowComparisonCanvas.png)

[Identify Flow Version Changes at a Glance](https://help.salesforce.com/s/articleView?id=release-notes.rn_automate_flow_builder_visual_flow_version_comparison.htm&release=262&type=5)

## Require Unanimous Approval for Approval Steps Assigned to Groups

The drive to feature parity with so called "Classic Approvals" continues, now we can do unanimous decisions for groups!

[Require Unanimous Approval for Approval Steps Assigned to Groups](https://help.salesforce.com/s/articleView?id=release-notes.rn_automate_automated_approvals_unanimous_approvals.htm&release=262&type=5)

### Honourable mention
**Approval Designers Can Now View Flow Dependencies** - I'll be honest I didn't know this permission set existed, basically users can make approval flows without the manage flows permission and with this release they can now view any flow dependencies.

[Approval Designers Can Now View Flow Dependencies](https://help.salesforce.com/s/articleView?id=release-notes.rn_automate_automated_approvals_designers_view_usage_details.htm&release=262&type=5)

> "Users with the Approval Designer permission can now view flow dependencies for their flow approval processes in the Approvals app. Previously, only users with the Manage Flow permission had access to this information."

## Avoid Manually Fixing Email Template References After Deploying Flows

No more breaking email templates on deployment! I'll let the release notes say it all:

> The action stores the selected template as a reference that persists across deployment environments. Previously, the Send Email action saved the selected email template as a template ID.

[Avoid Manually Fixing Email Template References After Deploying Flows Across Environments](https://help.salesforce.com/s/articleView?id=release-notes.rn_automate_flow_builder_persist_email_template_references_across_environments.htm&release=262&type=5)

I hope you get to check these flows features out in your orgs, there are some real gems in here! My personal favourite being that last one, no more email templates logged as IDs!
