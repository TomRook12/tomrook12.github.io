---
layout: post
title: "Flow Approvals Traps for new gamers"
date: 2025-08-26
author: tom
author_profile: /about/
categories: [technology, Salesforce, Flow]
image: /assets/images/FlowApprovalTraps/gowiththeflow.png
tags: [technology,  Salesforce, Flow]
---

Another flow approval post? I know! I am at the risk of turning this into a Flow Approval blog, I just love them so much. I thought I would share some of the things that I struggled to get my head around. 

# Little Things to Trip you Up
Minor annoyances? Slight issues? No matter what these things gave me pause and I wasn’t expecting them to work in this way…
## User Resource takes a Username not a User ID
![1approver.png]({{site.baseurl}}/assets/images/FlowApprovalTraps/1approver.png)

For an approval to run it needs a Queue, Group or User. The user takes a Username, Why on earth this is the case we may never know but a nice thing to trip you up! For the submitter you still need to pass in a user ID. Weird!
## Ugly Approval Screen
![uglyapprovalsonly.png]({{site.baseurl}}/assets/images/FlowApprovalTraps/uglyapprovalsonly.png)
On a record that I user has been assigned to approve, you need a work guide component that runs your approval screenflow. The Screenflow runs borderless except the title. Which is where my issue is, I would like some control over what is here. The API name of the flow? The breadcrumb trail of where they are? Why? What will an end user do with this information? Would be great if I could toggle it off (as in screen flows) or provide my own name(s), ideally using a resource. 
## Can’t launch the approval from a screenflow 
![noflowsinscreenflows.png]({{site.baseurl}}/assets/images/FlowApprovalTraps/noflowsinscreenflows.png)
I had this great idea that users would step through a screen flow and after sharing all of the details required for approval it would launch the approval workflow! Think capturing comments, reviewing required fields, maybe selecting an approver for use in the process. Well this isn’t possible! AS you can see in the screenshot just the approval subflows and legacy approvals are available. Not even launching as a subflow is allowed to work, a shame as classic approvals can be started in this way. I feel cut off from some major coolness and process improvement. 

*I would like to acknowledge the workaround here which is a screen flow that updates a record to launch a record triggered approval flow. This however feels CLUNKY and passing variables between the two flows requires fields to be created on the record. Not my favourite!*
## The Wizard only creates autolaunched
![wizard.png]({{site.baseurl}}/assets/images/FlowApprovalTraps/wizard.png)

The addition of a wizard to create approval flows in Summer ‘25 was a great feature enabling us to see how Salesforce wants these flows to be used but this creates an auto launched flow that can’t be launched directly from records meeting set criteria. Let me choose which approval flow is created! 
## The value from an approval is Approve or Reject 
![justapprove.png]({{site.baseurl}}/assets/images/FlowApprovalTraps/justapprove.png)
If you want to set up a decision based on the approval screen that salesforce gives OOB then the correct values that will be returned are approve and reject! I spent ages using Approved and Rejected and it wasn’t working… silly me! 
# Big Traps

## Workflow Item Mysteries 
![terribleerror.png]({{site.baseurl}}/assets/images/FlowApprovalTraps/terribleerror.png)
There are two issues here, first you NEED Workflow items on the page layout or the approval will fail - the error you get will not explain why. So just add it to the page layout when you start to build your flow for a given object. 


![approvalworkitems.png]({{site.baseurl}}/assets/images/FlowApprovalTraps/approvalworkitems.png)
Secondly, if you choose to add the approval trace component to see where and how the approval has progressed (mirroring approval history from classic approvals) users will only see approval steps they completed ( how useful…) You need to provide access to the Approval Submission and the ApprovalWorkItem object in their permissions (Approval Work Item has a master-detail relationship with Approval Submission). This is for anyone who wants to see this information. kind of cool you can hide this but also kind of tripped me up because why couldn’t my users see approval history?

## Setting up a button to submit is more lengthy than I would like
Sometimes it is nice to give users the option to launch the approval from a button, this can give a lot of flex to the approval process allowing a user to start it when they see fit. Getting an approval process to run from a button presents more obstacles than seems necessary, you need decent knowledge of setting up buttons particularly passing in variables and users can’t add comments at time of submission a separate field needs to be created. 

Checkout this tutorial by Salesforce break: https://salesforcebreak.com/2025/03/18/start-autolaunched-flow-approvals-from-a-button/

## Errors Suck
MY GOSH WHAT IS GOING ON HERE. A sea of SOAP API errors. The errors from these orchestrations are essentially useless with precisely zero information on how or why it failed, coupled with the fact you can’t debug an orchestration only view the error emails (usually in floods of tears as you get the same email for the 40th time in a row) it makes trouble shooting of any kind very frustrating. Set your error paths up and try and catch as much as you can in a custom field on the record.

Actually this last one might about to be fixed in Winter '26! Keep your eyes out! 

That is it really, was this really a helpful post or a chance for me to get somethings off my chest? Cast them into the world? Let me know what you think and what tripped you up when you first started working with approval flows.